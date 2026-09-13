"""
주간 파이프라인 — 매주 토요일 KST 09:00 GitHub Actions 실행 (미국장 금요일 마감 후).
1. 유니버스(S&P 500 + Nasdaq-100) 스냅샷
2. 신호 생성: M1 13F / M2 섹터 추정치 / M3 실적개선 / M4 흑자전환 / M5 Form 4 / M6 사이클
3. 정량 점수 → 보유 + 신규 후보 선정 → 상세 데이터
4. Claude 심층분석 + 시장 브리핑 → 신규편입/유지/제외 결정 → 이력 갱신
출력: data/weekly_signals.json, data/picks_history.json, data/reports/<주차>.json
"""
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import analyst
from data_fetcher import fetch_prices
from market_data import fetch_details, fetch_snapshots
from picks import (cache_entry, decide, fresh_analysis_reason, load_cache, load_history, pick_candidates,
                   quant_scores, save_cache, save_history, signal_hits, update_history)
from sec_data import fetch_13f, fetch_insider_trades
from signals import CAPEX_TICKERS, SECTOR_KR, build_m2, build_m3, build_m4, build_m6, m3_section, m4_section
from universe import load_universe

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
KST = timezone(timedelta(hours=9))


def _pct(v, n=1):
    return None if v is None else round(v * 100, n)


def _b(v):
    return None if v is None else round(v / 1e9, 2)


def build_dossier(tk, snaps, details, scores, hits, holding, today):
    s, d, q = snaps[tk], details.get(tk, {}), scores.get(tk, {})
    dossier = {
        "ticker": tk, "name": s["name"], "sector": SECTOR_KR.get(s["sector"], s["sector"]),
        "industry": s.get("industry"), "as_of": today,
        "price": s.get("price"), "market_cap_b": _b(s["market_cap"]),
        "valuation": {
            "trailing_pe": s.get("trailing_pe"), "forward_pe": s.get("forward_pe"), "peg": s.get("peg"),
            "fcf_yield_pct": q.get("fcf_yield_pct"), "analyst_target_mean": s.get("target_mean"),
            "analyst_rating_mean_1buy_5sell": s.get("rec_mean"), "analysts": s.get("analysts"),
        },
        "growth_profitability": {
            "gross_margin_pct": _pct(s.get("gross_margin")), "op_margin_pct": _pct(s.get("op_margin")),
            "roe_pct": _pct(s.get("roe")),
            "revenue_growth_last_q_yoy_pct": _pct(s.get("revenue_growth")),
            "eps_growth_last_q_yoy_pct": _pct(s.get("earnings_growth")),
            "eps_growth_est_this_fy_pct": _pct(s.get("growth_0y")),
            "eps_growth_est_next_fy_pct": _pct(s.get("growth_1y")),
        },
        "cash_debt_dilution": {
            "fcf_ttm_b": _b(d.get("fcf_ttm")), "sbc_ttm_b": _b(d.get("sbc_ttm")), "buyback_ttm_b": _b(d.get("buyback_ttm")),
            "fcf_margin_pct": q.get("fcf_margin_pct"), "net_debt_to_ebitda": q.get("net_debt_ebitda"),
            "share_count_change_pct": d.get("share_change_pct"), "share_count_span": d.get("share_change_span"),
        },
        "estimate_revisions_next_fy_eps": {
            "current": s.get("eps_next_fy"), "chg_7d_pct": s.get("rev_7d") and round(s["rev_7d"], 2),
            "chg_30d_pct": s.get("rev_30d") and round(s["rev_30d"], 2), "chg_90d_pct": s.get("rev_90d") and round(s["rev_90d"], 2),
            "up_revisions_30d": s.get("up_30d"), "down_revisions_30d": s.get("down_30d"),
        },
        "quarterly": {
            "periods": [p for p, _ in d.get("q_revenue", [])],
            "revenue_b": [_b(v) for _, v in d.get("q_revenue", [])],
            "op_margin_pct": [v for _, v in d.get("q_op_margin", [])],
            "diluted_eps": [v for _, v in d.get("q_eps", [])],
        },
        "annual_revenue_b": [[p, _b(v)] for p, v in d.get("y_revenue", [])],
        "eps_surprises": d.get("eps_surprises", []),
        "next_earnings": d.get("next_earnings"),
        "return_1y_pct": d.get("return_1y_pct"), "from_52w_high_pct": d.get("from_52w_high_pct"),
        "quant_score": {k: q.get(k) for k in ("score", "quality", "health", "value", "revisions")},
        "dashboard_signals": hits,
        "holding": None,
    }
    if holding:
        price = s.get("price")
        dossier["holding"] = {
            "added_date": holding.get("added_date"), "added_price": holding.get("added_price"),
            "return_since_add_pct": round((price / holding["added_price"] - 1) * 100, 1)
            if price and holding.get("added_price") else None,
            "original_thesis": holding.get("thesis"), "thesis_breakers": holding.get("thesis_breakers"),
        }
    return dossier


def main():
    now = datetime.now(KST)
    today, week = now.date().isoformat(), now.strftime("%G-W%V")
    os.makedirs(os.path.join(DATA_DIR, "reports"), exist_ok=True)

    universe = load_universe()
    snaps = fetch_snapshots(universe)
    spy = fetch_prices(["SPY"]).get("SPY")

    m1 = fetch_13f()
    m5 = fetch_insider_trades(sorted(snaps))
    m2 = build_m2(snaps)
    m3_tk, m4_tk = build_m3(snaps), build_m4(snaps)
    scores = quant_scores(snaps)

    hist = load_history()
    held_tk, new_tk = pick_candidates(scores, snaps, hist["portfolio"], m1, m3_tk, m5)
    details = fetch_details(held_tk + new_tk + m3_tk + m4_tk + CAPEX_TICKERS)
    m6 = build_m6(snaps, details)

    weekly = {
        "built_at_kst": now.strftime("%Y-%m-%d %H:%M"), "week": week, "universe_size": len(snaps),
        "m1": m1, "m2": m2, "m3": m3_section(m3_tk, snaps, details), "m4": m4_section(m4_tk, snaps, details),
        "m5": m5, "m6": m6, "market_brief": None,
        "status": {"sec": m1 is not None and m5 is not None, "claude": analyst.available()},
    }

    if analyst.available():
        weekly["market_brief"] = analyst.market_brief({
            "as_of": today,
            "sector_eps_revisions_30d": [{"sector": x["sector_kr"], "chg_pct": x["eps_revision_pct_30d"], "momentum": x["momentum"]}
                                         for x in m2["sectors"]],
            "cycle_indicators": m6["overall"],
            "current_portfolio": [h["ticker"] for h in hist["portfolio"]],
        })

        holding_by_tk = {h["ticker"]: h for h in hist["portfolio"]}
        dossiers = [build_dossier(tk, snaps, details, scores, signal_hits(tk, m1, m3_tk, m5), holding_by_tk.get(tk), today)
                    for tk in held_tk + new_tk]

        # 변화 없는 종목은 지난 분석 재사용 (비용 절감)
        cache = load_cache()
        fresh_reason = {d["ticker"]: fresh_analysis_reason(cache.get(d["ticker"]), snaps[d["ticker"]],
                                                           holding_by_tk.get(d["ticker"]), today) for d in dossiers}
        to_run = [d for d in dossiers if fresh_reason[d["ticker"]]]
        reused = {tk: cache[tk] for tk, r in fresh_reason.items() if r is None}
        print(f"심층분석 대상 {len(dossiers)}종목 (보유 {len(held_tk)} + 후보 {len(new_tk)}) → 신규 분석 {len(to_run)} / 재사용 {len(reused)}")
        with ThreadPoolExecutor(max_workers=3) as ex:
            fresh = dict(zip([d["ticker"] for d in to_run], ex.map(analyst.analyze_stock, to_run)))
        analyses = {**{tk: c["analysis"] for tk, c in reused.items()}, **fresh}

    if analyst.available() and fresh and all(a is None for a in fresh.values()):
        # API 키·요청 오류 등 전면 실패: 추천 이력을 '분석 실패' 기록으로 오염시키지 않고 신호만 배포
        print("::error::Claude 심층분석이 전부 실패 — 추천 이력 갱신 건너뜀 (API 키·요청 오류 확인)")
        weekly["status"]["claude"] = False
    elif analyst.available():
        for tk, a in fresh.items():
            if a is not None:
                cache[tk] = cache_entry(a, snaps[tk], details.get(tk, {}), today)
        save_cache(cache, today)

        kept, decisions, removed = decide(hist["portfolio"], new_tk, analyses, snaps, scores, today)
        for dcs in decisions:
            if dcs["ticker"] in reused:
                dcs["reason"] = (f"[{reused[dcs['ticker']]['analyzed_date']} 분석 재사용 — 이후 실적 발표·큰 주가 변동·"
                                 f"추정치 급변 없음] " + dcs["reason"])
        hist = update_history(hist, week, today, kept, decisions, removed, snaps, spy)
        save_history(hist)

        dossier_by_tk = {d["ticker"]: d for d in dossiers}
        report = {
            "week": week, "date": today, "spy_price": spy,
            "candidates": [{"ticker": tk, "role": "보유" if tk in held_tk else "신규후보", **scores[tk],
                            "analysis": "재사용" if tk in reused else fresh_reason[tk]} for tk in held_tk + new_tk],
            "analyses": {tk: {"analysis": a, "metrics": {k: v for k, v in dossier_by_tk[tk].items() if k != "holding"},
                              "reused_from": reused[tk]["analyzed_date"] if tk in reused else None}
                         for tk, a in analyses.items()},
            "decisions": decisions,
            "usage": analyst.usage_summary(),
        }
        with open(os.path.join(DATA_DIR, "reports", f"{week}.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        print("결정:", [(x["ticker"], x["action"]) for x in decisions])
        print("Claude 사용량:", report["usage"])
    else:
        print("ANTHROPIC_API_KEY 미설정 — 심층분석·뉴스·추천 갱신 건너뜀")

    with open(os.path.join(DATA_DIR, "weekly_signals.json"), "w", encoding="utf-8") as f:
        json.dump(weekly, f, ensure_ascii=False, indent=1)
    print("주간 파이프라인 완료")


if __name__ == "__main__":
    main()
