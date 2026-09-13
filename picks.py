"""
6개월+ 보유 목적 주간 추천 엔진.
1) quant_scores   : 유니버스 정량 점수 (품질·재무건전성·가격매력·추정치 흐름, 퍼센타일 기반)
2) pick_candidates: 기존 보유 + 신규 후보 상위 N
3) decide         : Claude 심층분석 결과 → 신규편입/유지/제외 (규칙 기반, 억지 편입 없음)
4) 이력 파일(data/picks_history.json) 갱신
"""
import json
import os
from datetime import date, timedelta

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_PATH = os.path.join(BASE_DIR, "data", "picks_history.json")
CACHE_PATH = os.path.join(BASE_DIR, "data", "analysis_cache.json")

REUSE_MAX_DAYS = 28         # 이 기간 안의 분석은 변화가 없으면 재사용
REUSE_PRICE_MOVE = 0.15     # 분석 시점 대비 주가 ±15% 이상 → 재분석
REUSE_EPS_MOVE = 0.05       # 내년 EPS 컨센서스 ±5% 이상 변화 → 재분석

MAX_HOLDINGS = 5
MAX_PER_SECTOR = 2
NEW_CANDIDATES = 8
MIN_CONVICTION_NEW = 4      # 신규 편입 최소 확신도 (1~5)
SWAP_CONVICTION = 5         # 만석일 때 교체하려면 후보 확신도 5 + 기존 종목 '약화'·확신도 3 이하


# ── 1. 정량 점수 ──────────────────────────────────────────────────
def _rank(series, higher_better=True, by=None):
    """퍼센타일(0~1). by 지정 시 그룹(섹터) 내 순위. 결측은 0.5(중립)."""
    if by is None:
        r = series.rank(pct=True, ascending=higher_better)
    else:
        r = series.groupby(by).rank(pct=True, ascending=higher_better)
    return r.fillna(0.5)


def quant_scores(snaps):
    df = pd.DataFrame(snaps.values()).set_index("ticker")
    fcf_margin = df["fcf"] / df["revenue"]
    fcf_yield = df["fcf"] / df["market_cap"]
    net_debt_ebitda = (df["total_debt"].fillna(0) - df["total_cash"].fillna(0)) / df["ebitda"].where(df["ebitda"] > 0)
    fwd_pe = df["forward_pe"].where(df["forward_pe"] > 0)
    peg = df["peg"].where(df["peg"] > 0)
    breadth = (df["up_30d"].fillna(0) - df["down_30d"].fillna(0)) / (df["up_30d"].fillna(0) + df["down_30d"].fillna(0)).replace(0, float("nan"))

    quality = (_rank(df["gross_margin"]) + _rank(df["op_margin"]) + _rank(df["roe"].clip(-1, 1))
               + _rank(fcf_margin) + _rank(df["revenue_growth"]) + _rank(df["growth_1y"])) / 6
    fcf_positive = (fcf_margin > 0).astype(float).where(fcf_margin.notna())
    health = (_rank(net_debt_ebitda, higher_better=False) + _rank(fcf_positive)) / 2
    value = (_rank(fwd_pe, higher_better=False, by=df["sector"]) + _rank(fcf_yield, by=df["sector"])
             + _rank(peg, higher_better=False)) / 3
    revisions = (_rank(df["rev_30d"]) + _rank(df["rev_90d"]) + _rank(breadth)) / 3

    total = (quality * 0.30 + health * 0.20 + value * 0.25 + revisions * 0.25) * 100
    eligible = (df["forward_eps"] > 0) & (df["op_margin"].fillna(0) > 0) & (df["analysts"].fillna(0) >= 5)

    out = {}
    for tk in df.index:
        out[tk] = {
            "score": round(float(total[tk]), 1),
            "quality": round(float(quality[tk]) * 100), "health": round(float(health[tk]) * 100),
            "value": round(float(value[tk]) * 100), "revisions": round(float(revisions[tk]) * 100),
            "eligible": bool(eligible[tk]),
            "fcf_margin_pct": None if pd.isna(fcf_margin[tk]) else round(float(fcf_margin[tk]) * 100, 1),
            "fcf_yield_pct": None if pd.isna(fcf_yield[tk]) else round(float(fcf_yield[tk]) * 100, 2),
            "net_debt_ebitda": None if pd.isna(net_debt_ebitda[tk]) else round(float(net_debt_ebitda[tk]), 2),
        }
    return out


# ── 2. 후보 선정 ──────────────────────────────────────────────────
def signal_hits(tk, m1, m3_tickers, m5):
    hits = []
    if m1:
        gurus = [inv["investor"] for inv in m1["investors"] if any(r["ticker"] == tk for r in inv["top10"])]
        if gurus:
            hits.append("M1 대가 상위보유: " + ", ".join(gurus))
    if tk in m3_tickers:
        hits.append("M3 실적 개선 기업")
    if m5 and tk in m5.get("buy_tickers", []):
        hits.append("M5 내부자 장내 매수")
    return hits


def pick_candidates(scores, snaps, holdings, m1, m3_tickers, m5):
    """보유 종목 전부 + 신규 후보 상위 NEW_CANDIDATES (신호 적중 시 가산점)."""
    held = {h["ticker"] for h in holdings}
    ranked = []
    for tk, sc in scores.items():
        if tk in held or not sc["eligible"]:
            continue
        hits = signal_hits(tk, m1, m3_tickers, m5)
        ranked.append((sc["score"] + 3 * len(hits), tk))
    ranked.sort(reverse=True)
    return [h["ticker"] for h in holdings if h["ticker"] in snaps], [tk for _, tk in ranked[:NEW_CANDIDATES]]


# ── 2-1. 분석 재사용 (비용 절감) ─────────────────────────────────
def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache, today):
    """오래된 항목(REUSE_MAX_DAYS×2 초과) 정리 후 저장."""
    cutoff = (date.fromisoformat(today) - timedelta(days=REUSE_MAX_DAYS * 2)).isoformat()
    cache = {tk: c for tk, c in cache.items() if c["analyzed_date"] >= cutoff}
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)


def cache_entry(analysis, snap, detail, today):
    return {"analyzed_date": today, "price": snap.get("price"), "eps_next_fy": snap.get("eps_next_fy"),
            "next_earnings": detail.get("next_earnings"), "analysis": analysis}


def fresh_analysis_reason(entry, snap, holding, today):
    """재분석이 필요하면 사유 문자열, 재사용 가능하면 None."""
    if not entry:
        return "첫 분석"
    if (date.fromisoformat(today) - date.fromisoformat(entry["analyzed_date"])).days >= REUSE_MAX_DAYS:
        return f"지난 분석 {REUSE_MAX_DAYS}일 경과"
    if entry.get("next_earnings") and entry["next_earnings"] <= today:
        return "분석 이후 실적 발표"
    price, old_price = snap.get("price"), entry.get("price")
    if price and old_price and abs(price / old_price - 1) >= REUSE_PRICE_MOVE:
        return f"분석 이후 주가 {(price / old_price - 1) * 100:+.0f}%"
    eps, old_eps = snap.get("eps_next_fy"), entry.get("eps_next_fy")
    if eps and old_eps and abs(eps / old_eps - 1) >= REUSE_EPS_MOVE:
        return f"분석 이후 내년 EPS 추정치 {(eps / old_eps - 1) * 100:+.1f}%"
    if holding and holding.get("thesis_status") == "약화":
        return "보유 논리 약화 — 매주 재점검"
    return None


# ── 3. 결정 ──────────────────────────────────────────────────────
def decide(holdings, new_candidates, analyses, snaps, scores, today):
    """
    analyses: {ticker: 분석 dict | None}
    반환: (새 보유 목록, 결정 로그, 교체로 빠진 종목)
    """
    decisions, kept, removed = [], [], []
    sector = lambda tk: snaps.get(tk, {}).get("sector", "Unknown")

    for h in holdings:
        a = analyses.get(h["ticker"])
        if a is None:
            kept.append(h)
            decisions.append({"ticker": h["ticker"], "action": "유지",
                              "reason": "이번 주 분석을 완료하지 못해 기존 판단을 유지합니다 (데이터·API 오류)."})
            continue
        status = a.get("thesis_status")
        own_status = status not in (None, "해당없음")
        if not own_status:  # 편입 전 후보 시절 분석을 재사용한 경우 기존 상태 유지
            status = h.get("thesis_status") or "유효"
        reason = (own_status and a.get("thesis_status_reason")) or a["verdict_reason"]
        if status == "붕괴" or a["verdict"] == "부적합":
            removed.append(h)
            decisions.append({"ticker": h["ticker"], "action": "제외", "reason": reason})
        else:
            h = {**h, "last_review": today, "thesis_status": status, "conviction": a["conviction"]}
            kept.append(h)
            note = " (논리 약화 — 관찰 강화)" if status == "약화" else ""
            decisions.append({"ticker": h["ticker"], "action": "유지", "reason": reason + note})

    qualified = [tk for tk in new_candidates
                 if analyses.get(tk) and analyses[tk]["verdict"] == "편입 적합"
                 and analyses[tk]["conviction"] >= MIN_CONVICTION_NEW]
    qualified.sort(key=lambda tk: (-analyses[tk]["conviction"], -scores[tk]["score"]))

    def sector_count(tk):
        return sum(1 for x in kept if sector(x["ticker"]) == sector(tk))

    for tk in qualified:
        a = analyses[tk]
        if sector_count(tk) >= MAX_PER_SECTOR:
            decisions.append({"ticker": tk, "action": "보류", "reason":
                              f"편입 적합 판정이지만 같은 섹터({sector(tk)}) 보유가 이미 {MAX_PER_SECTOR}종목이라 분산을 위해 보류."})
            continue
        if len(kept) >= MAX_HOLDINGS:
            weak = sorted([x for x in kept if x.get("thesis_status") == "약화" and (x.get("conviction") or 5) <= 3],
                          key=lambda x: x.get("conviction") or 5)
            if a["conviction"] >= SWAP_CONVICTION and weak:
                out = weak[0]
                kept.remove(out)
                removed.append(out)
                for dcs in decisions:
                    if dcs["ticker"] == out["ticker"]:
                        dcs["action"], dcs["reason"] = "제외", (
                            f"투자 논리가 약화된 상태에서 확신도가 더 높은 {tk}로 교체. 기존 판단: {dcs['reason']}")
            else:
                decisions.append({"ticker": tk, "action": "보류", "reason":
                                  f"편입 적합(확신도 {a['conviction']})이나 포트폴리오 {MAX_HOLDINGS}자리가 모두 유효한 논리로 채워져 있어 보류."})
                continue
        s = snaps[tk]
        kept.append({
            "ticker": tk, "name": s["name"], "sector": s["sector"],
            "added_date": today, "added_price": s.get("price"),
            "thesis": a["one_line_thesis"], "thesis_breakers": a["bear_case"]["thesis_breakers"],
            "conviction": a["conviction"], "thesis_status": "유효", "last_review": today,
        })
        decisions.append({"ticker": tk, "action": "신규편입", "reason": a["verdict_reason"]})

    for tk in new_candidates:
        if tk in qualified:
            continue
        a = analyses.get(tk)
        if a is None:
            reason = "분석 실패로 판단 보류."
        elif a["verdict"] == "편입 적합":
            reason = f"편입 적합이나 확신도 {a['conviction']}로 기준({MIN_CONVICTION_NEW}) 미달. {a['verdict_reason']}"
        else:
            reason = f"[{a['verdict']}] {a['verdict_reason']}"
        decisions.append({"ticker": tk, "action": "미편입", "reason": reason})
    return kept, decisions, removed


# ── 4. 이력 ──────────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"portfolio": [], "closed": [], "weeks": []}


def save_history(hist):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=1)


def update_history(hist, week, today, kept, decisions, removed, snaps, spy_price):
    for h in kept:
        if h.get("added_date") == today and h.get("spy_at_add") is None:
            h["spy_at_add"] = spy_price
    for h in removed:
        price = snaps.get(h["ticker"], {}).get("price")
        reason = next((d["reason"] for d in decisions if d["ticker"] == h["ticker"] and d["action"] == "제외"), "")
        hist["closed"].append({
            "ticker": h["ticker"], "name": h.get("name"), "added_date": h.get("added_date"), "removed_date": today,
            "added_price": h.get("added_price"), "removed_price": price,
            "return_pct": round((price / h["added_price"] - 1) * 100, 1) if price and h.get("added_price") else None,
            "spy_return_pct": round((spy_price / h["spy_at_add"] - 1) * 100, 1) if spy_price and h.get("spy_at_add") else None,
            "reason": reason,
        })
    hist["portfolio"] = kept
    hist["weeks"] = [w for w in hist["weeks"] if w["week"] != week]
    hist["weeks"].append({"week": week, "date": today, "decisions": decisions,
                          "portfolio_after": [h["ticker"] for h in kept]})
    return hist
