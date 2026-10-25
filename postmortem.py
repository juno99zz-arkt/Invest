"""
월간 신호 검증 (매달 마지막 금요일, 정기 메일에 포함).
방법론: tradermonty/claude-trading-skills 의 signal-postmortem(신호별 결과 분류) +
weekly-performance-digest(승률·기대값·손익비 요약)를 이 계좌(6개월+ 장기, 최대 5종목+현금)에 맞게 옮김.

신호 (모두 기록 기반, 사후 선택 없음)
  LONG  : 편입(보유 이력), 신규편입·탐색 편입·공포 구간 편입, 비중 확대, 공포·탐욕 20/10/5 [매수 신호](SPY 기준)
  SHORT : 제외, 비중 축소, [매도 경고](가격)  — '이후 SPY 보다 못했는가'로 평가
  미실행 LONG : 미편입·보류 후보 → 이후 SPY 대비 +2% 이상이면 MISSED_OPPORTUNITY (필터가 너무 보수적인지)
진입가 = 신호 다음 거래일 시가 (가상 계좌 체결 규칙과 동일). 평가 기간 5·20·60 거래일.
수익률 = 종목 신호는 SPY 대비 초과수익(종목 선택 능력), 시장 신호(공포·탐욕)는 SPY 절대수익.
분류 (signal-postmortem 결정 트리): 미실행 → MISSED_OPPORTUNITY / SKIPPED_OK,
  국면 변화(VIX: <20 RISK_ON, >25 RISK_OFF) + 반대 방향 2%↑ 손실 → REGIME_MISMATCH,
  |수익| < 문턱(5일 0.5%, 20일 1%, 60일 2%) → NEUTRAL, 방향 일치 → TRUE_POSITIVE, 불일치 → FALSE_POSITIVE(MILD/SEVERE).
요약 (weekly-performance-digest): 승률, 기대값(방향 반영 평균 수익), 손익비(이익 합/손실 합), 최고·최악.
공포·탐욕 문턱 검증: 지수 이력(누적 저장)에서 20/10/5 하향 돌파일 이후 SPY 5·20·60일 수익 vs 전체 평균.
표본 20건 미만이면 '참고용' — 규칙 변경은 제안만 하고 자동 적용하지 않는다.

  python postmortem.py --auto   : 오늘(KST)이 그 달 마지막 금요일이면 실행
  python postmortem.py --force  : 즉시 실행
출력: data/postmortem/<YYYY-MM>.json (메일·대시보드용)
"""
import glob
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(DATA_DIR, "postmortem")
FG_HIST = os.path.join(DATA_DIR, "fear_history.json")
KST = timezone(timedelta(hours=9))
HORIZONS = (5, 20, 60)
THRESH = {5: 0.5, 20: 1.0, 60: 2.0}
MIN_SAMPLE = 20
BENCH, VIX = "SPY", "^VIX"


def _load(p, d):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return d


def is_last_friday(d):
    return d.weekday() == 4 and (d + timedelta(days=7)).month != d.month


# ── 신호 수집 ─────────────────────────────────────────────────────
def collect_signals(hist, push_log):
    sigs, seen = [], set()

    def add(**s):
        k = (s["ticker"], s["date"], s["direction"], s["source"])
        if k not in seen:
            seen.add(k)
            sigs.append(s)

    for h in hist.get("portfolio", []) + hist.get("closed", []):
        if h.get("added_date"):
            add(ticker=h["ticker"], date=h["added_date"], direction="LONG", source="편입", taken=True)
        if h.get("removed_date"):
            add(ticker=h["ticker"], date=h["removed_date"], direction="SHORT", source="제외", taken=True)
    weeks = sorted(hist.get("weeks", []), key=lambda w: (w["date"], w.get("interim", False)))
    last_skip = {}  # 매일 분석: 같은 미편입 후보를 매일 세지 않도록 7일에 1건만
    for i, w in enumerate(weeks):
        prev = next((x.get("weights") for x in reversed(weeks[:i]) if x.get("weights")), None) or {}
        cur = w.get("weights") or {}
        for d in w.get("decisions", []):
            r = d.get("reason", "")
            if d["action"] == "신규편입":
                src = "공포 구간 편입" if "공포 구간" in r or "공포·탐욕" in r else "탐색 편입" if "[탐색 편입]" in r else "편입"
                add(ticker=d["ticker"], date=w["date"], direction="LONG", source=src, taken=True)
            elif d["action"] == "제외":
                add(ticker=d["ticker"], date=w["date"], direction="SHORT", source="제외", taken=True)
            elif d["action"] in ("미편입", "보류"):
                ls = last_skip.get(d["ticker"])
                if ls and (date.fromisoformat(w["date"]) - date.fromisoformat(ls)).days < 7:
                    continue
                last_skip[d["ticker"]] = w["date"]
                add(ticker=d["ticker"], date=w["date"], direction="LONG",
                    source="관심종목 미편입" if "[관심종목]" in r else "미편입·보류", taken=False)
        if w.get("weights") is not None and prev:
            for tk in set(prev) | set(cur):
                a, b = prev.get(tk, 0), cur.get(tk, 0)
                if a and b > a:
                    add(ticker=tk, date=w["date"], direction="LONG", source="비중 확대", taken=True)
                elif a and 0 < b < a:
                    add(ticker=tk, date=w["date"], direction="SHORT", source="비중 축소", taken=True)
    for k, v in (push_log.get("sent") or {}).items():
        m = re.match(r"^([A-Z.\-^]+):(약세도달|급락|편입가하락):", k)
        if m:
            add(ticker=m.group(1), date=str(v)[:10], direction="SHORT", source="매도 경고", taken=False, warn=True)
    return sigs


# ── 가격 ─────────────────────────────────────────────────────────
def fetch_prices(tickers, start):
    import yfinance as yf
    out = {}
    for tk in sorted(set(tickers)):
        try:
            df = yf.Ticker(tk).history(start=start, auto_adjust=True)
            if df is not None and not df.empty:
                out[tk] = [(i.strftime("%Y-%m-%d"), float(r["Open"]), float(r["Close"])) for i, r in df.iterrows()]
        except Exception as e:
            print(f"  시세 실패 {tk}: {e}")
    return out


def _entry_idx(series, d):
    """신호일 다음 거래일 인덱스 (시가 체결)."""
    for i, (dd, _, _) in enumerate(series):
        if dd > d:
            return i
    return None


def _regime(vix):
    return None if vix is None else "RISK_ON" if vix < 20 else "RISK_OFF" if vix > 25 else "TRANSITION"


def evaluate(sig, px):
    s, b, v = px.get(sig["ticker"]), px.get(BENCH), px.get(VIX)
    market = sig["ticker"] == BENCH
    if not s or not b:
        return {**sig, "status": "가격 없음"}
    i = _entry_idx(s, sig["date"])
    if i is None:
        return {**sig, "status": "진입 전"}
    ent_d, ent = s[i][0], s[i][1]
    bi = next((k for k, x in enumerate(b) if x[0] >= ent_d), None)
    vd = {x[0]: x[2] for x in (v or [])}
    rec = {**sig, "entry_date": ent_d, "entry_price": round(ent, 2), "returns": {}, "outcomes": {}}
    vix0 = vd.get(ent_d)
    rec["regime_at_signal"] = _regime(vix0)
    for h in HORIZONS:
        j = i + h - 1
        if j >= len(s) or bi is None or bi + h - 1 >= len(b):
            rec["outcomes"][h] = "PENDING"
            continue
        r = s[j][2] / ent - 1
        br = b[bi + h - 1][2] / b[bi][1] - 1
        x = (r if market else r - br) * 100
        rec["returns"][h] = {"abs_pct": round(r * 100, 2), "excess_pct": round(x, 2)}
        skipped = not sig.get("taken", True) and not sig.get("warn")
        # 미실행 후보는 '필터 판단' 관점: SPY 보다 못했으면 + (피한 손실), 앞섰으면 − (놓친 수익)
        signed = -x if skipped or sig["direction"] == "SHORT" else x
        reg1 = _regime(vd.get(s[j][0]))
        if skipped:
            cat = "MISSED_OPPORTUNITY" if x >= 2 else "SKIPPED_OK"
        elif rec["regime_at_signal"] and reg1 and reg1 != rec["regime_at_signal"] and signed < -2:
            cat = "REGIME_MISMATCH"
        elif abs(x) < THRESH[h]:
            cat = "NEUTRAL"
        elif signed > 0:
            cat = "TRUE_POSITIVE"
        else:
            cat = "FALSE_POSITIVE_SEVERE" if signed < -2 else "FALSE_POSITIVE_MILD"
        rec["outcomes"][h] = cat
        rec.setdefault("signed", {})[h] = round(signed, 2)
    return rec


def summarize(recs, h):
    """weekly-performance-digest 식 요약 (방향 반영 수익 기준)."""
    rows = [r for r in recs if (r.get("outcomes") or {}).get(h) not in (None, "PENDING")]
    if not rows:
        return {"n": 0}
    xs = [r["signed"][h] for r in rows]
    cats = [r["outcomes"][h] for r in rows]
    win = sum(1 for c in cats if c in ("TRUE_POSITIVE", "SKIPPED_OK"))
    loss = sum(1 for c in cats if c.startswith("FALSE_POSITIVE") or c in ("REGIME_MISMATCH", "MISSED_OPPORTUNITY"))
    gains, losses = sum(x for x in xs if x > 0), -sum(x for x in xs if x < 0)
    best, worst = max(rows, key=lambda r: r["signed"][h]), min(rows, key=lambda r: r["signed"][h])
    return {"n": len(rows), "win_rate": round(win / (win + loss), 2) if win + loss else None,
            "expectancy_pct": round(sum(xs) / len(xs), 2),
            "profit_factor": round(gains / losses, 2) if losses else None,
            "categories": {c: cats.count(c) for c in sorted(set(cats))},
            "best": f"{best['ticker']} {best['date']} {best['signed'][h]:+.1f}%",
            "worst": f"{worst['ticker']} {worst['date']} {worst['signed'][h]:+.1f}%",
            "reliable": len(rows) >= MIN_SAMPLE}


# ── 공포·탐욕 문턱 검증 ────────────────────────────────────────────
def fear_history():
    """CNN 이력(최근 1년)을 누적 저장해 시간이 갈수록 표본을 늘린다."""
    store = _load(FG_HIST, {})
    cur = _load(os.path.join(DATA_DIR, "fear_greed.json"), {}) or {}
    for p in cur.get("history") or []:
        store[p["d"]] = p["v"]
    if store:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(FG_HIST, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(store.items())), f)
    return sorted(store.items())


def fear_study(hist_fg, px):
    b = px.get(BENCH) or []
    if len(hist_fg) < 30 or not b:
        return None

    def fwd(d, h):
        i = _entry_idx(b, d)
        if i is None or i + h - 1 >= len(b):
            return None
        return (b[i + h - 1][2] / b[i][1] - 1) * 100

    base = {h: [x for x in (fwd(d, h) for d, _ in hist_fg) if x is not None] for h in HORIZONS}
    out = {"period": f"{hist_fg[0][0]} ~ {hist_fg[-1][0]}", "days": len(hist_fg),
           "baseline": {h: round(sum(v) / len(v), 2) if v else None for h, v in base.items()}, "levels": []}
    for lv in (20, 10, 5):
        crosses = [hist_fg[i][0] for i in range(1, len(hist_fg)) if hist_fg[i][1] < lv <= hist_fg[i - 1][1]]
        row = {"level": lv, "crossings": crosses, "n": len(crosses)}
        for h in HORIZONS:
            v = [x for x in (fwd(d, h) for d in crosses) if x is not None]
            row[f"avg_{h}d"] = round(sum(v) / len(v), 2) if v else None
            row[f"hit_{h}d"] = round(sum(1 for x in v if x > 0) / len(v), 2) if v else None
            row[f"n_{h}d"] = len(v)
        bl = out["baseline"].get(20)
        if row["n_20d"] == 0:
            row["verdict"] = "이력 기간 중 돌파 없음 — 판단 보류"
        elif bl is not None and row["avg_20d"] is not None:
            edge = row["avg_20d"] - bl
            tag = "유의미해 보임" if edge >= 1 else "평균과 비슷" if edge > -1 else "오히려 부진"
            row["verdict"] = (f"돌파 후 20일 SPY {row['avg_20d']:+.1f}% vs 평소 {bl:+.1f}% ({edge:+.1f}%p, {tag})"
                              + (f" · 표본 {row['n_20d']}건이라 참고용" if row["n_20d"] < MIN_SAMPLE else ""))
        out["levels"].append(row)
    return out


def suggestions(groups, fs):
    """규칙 조정 제안 (자동 적용 안 함)."""
    out = []
    for name, g in groups.items():
        s = g.get(20) or {}
        if not s.get("n"):
            continue
        rel = "" if s.get("reliable") else f" (표본 {s['n']}건, 참고용)"
        if name == "미편입·보류" and (s.get("categories") or {}).get("MISSED_OPPORTUNITY", 0) / s["n"] >= 0.4:
            out.append(f"미편입 후보 중 {s['categories']['MISSED_OPPORTUNITY']}/{s['n']}건이 20일 뒤 SPY 를 2%p 이상 앞섬 — 탐색 편입 문턱(최소 기대수익 10%)이 너무 보수적인지 검토{rel}")
        if name in ("편입", "탐색 편입", "공포 구간 편입") and s.get("expectancy_pct") is not None and s["expectancy_pct"] < -1:
            out.append(f"'{name}' 신호의 20일 초과수익 평균 {s['expectancy_pct']:+.1f}% — 편입 조건 강화 검토{rel}")
        if name == "매도 경고" and s.get("win_rate") is not None and s["win_rate"] < 0.4:
            out.append(f"매도 경고 이후 오히려 반등한 경우가 많음(적중 {s['win_rate']:.0%}) — 경고 문턱(−10%/−15%) 완화 검토{rel}")
    for row in (fs or {}).get("levels", []):
        if row.get("n_20d", 0) >= 3 and row.get("avg_20d") is not None and fs["baseline"].get(20) is not None:
            edge = row["avg_20d"] - fs["baseline"][20]
            if edge < -1:
                out.append(f"공포·탐욕 {row['level']} 돌파 후 성과가 평소보다 {edge:+.1f}%p 낮음 — {row['level']} 단계 가중 축소 검토")
    if not out:
        out.append("규칙 변경을 권할 만한 패턴 없음 — 현행 유지 (표본이 쌓이면 다시 판단)")
    return out


def run(today=None):
    today = today or datetime.now(KST).date()
    hist = _load(os.path.join(DATA_DIR, "picks_history.json"), {})
    push_log = _load(os.path.join(DATA_DIR, "push_log.json"), {})
    sigs = collect_signals(hist, push_log)
    fg = fear_history()
    for lv in (20, 10, 5):  # 실제 [매수 신호] 푸시 이력 → SPY LONG 신호
        for k in (push_log.get("sent") or {}):
            if k.startswith(f"fg:{lv}:"):
                sigs.append({"ticker": BENCH, "date": k.split(":")[2], "direction": "LONG",
                             "source": f"공포·탐욕 {lv}", "taken": True})
    start = min([s["date"] for s in sigs] + ([fg[0][0]] if fg else []) + [today.isoformat()])
    start = (date.fromisoformat(start) - timedelta(days=7)).isoformat()
    px = fetch_prices([s["ticker"] for s in sigs] + [BENCH, VIX], start)
    recs = [evaluate(s, px) for s in sigs]
    groups = {}
    for r in recs:
        groups.setdefault(r["source"], []).append(r)
    gsum = {name: {h: summarize(rs, h) for h in HORIZONS} for name, rs in groups.items()}
    taken = [r for r in recs if r.get("taken") and r["ticker"] != BENCH]
    skipped = [r for r in recs if not r.get("taken") and not r.get("warn")]
    fs = fear_study(fg, px)
    month = today.strftime("%Y-%m")
    month_recs = [r for r in recs if r["date"][:7] == month]
    out = {"generated": today.isoformat(), "month": month,
           "method": "signal-postmortem + weekly-performance-digest (tradermonty/claude-trading-skills) 방식, 장기 계좌용 5·20·60거래일",
           "n_signals": len(recs), "n_this_month": len(month_recs),
           "overall": {h: {"실행(편입·확대·축소·제외)": summarize(taken, h), "미실행 후보(필터 판단)": summarize(skipped, h)} for h in HORIZONS},
           "by_source": gsum, "fear_study": fs, "suggestions": suggestions(gsum, fs),
           "records": sorted(recs, key=lambda r: (r["date"], r["ticker"]), reverse=True)}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{month}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"월간 신호 검증 {month}: 신호 {len(recs)}건 (이번 달 {len(month_recs)})")
    for s in out["suggestions"]:
        print("  - " + s)
    return out


if __name__ == "__main__":
    now = datetime.now(KST).date()
    if "--force" in sys.argv or is_last_friday(now):
        run(now)
    else:
        print(f"{now} 는 마지막 금요일이 아님 — 월간 신호 검증 건너뜀")
