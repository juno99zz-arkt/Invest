"""
모델 비교 (1회성, 수동 실행): 같은 종목·같은 데이터로 Opus 5 와 Sonnet 5 심층분석을 나란히 생성.
- 종목: 정량 점수 상위 신규 후보 3개 (환경변수 COMPARE_TICKERS="AAA,BBB,CCC" 로 지정 가능)
- 출력: data/compare/latest.json (+ 날짜별 사본) → compare.html 에서 블라인드(A/B) 비교
"""
import json
import os
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import analyst
from market_data import fetch_details, fetch_snapshots
from picks import pick_candidates, quant_scores, signal_hits
from run_weekly import build_dossier
from signals import build_m3
from universe import load_universe

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "data", "compare")
MODELS = ["claude-opus-5", "claude-sonnet-5"]
KST = timezone(timedelta(hours=9))


def main():
    if not analyst.available():
        raise SystemExit("ANTHROPIC_API_KEY 미설정 — 비교 불가")
    today = datetime.now(KST).date().isoformat()

    snaps = fetch_snapshots(load_universe())
    scores = quant_scores(snaps)
    m3_tk = build_m3(snaps)
    override = [t.strip().upper() for t in os.environ.get("COMPARE_TICKERS", "").split(",") if t.strip()]
    tickers = [t for t in override if t in snaps] or pick_candidates(scores, snaps, [], None, m3_tk, None)[1][:3]
    print("비교 종목:", tickers)

    details = fetch_details(tickers)
    dossiers = {tk: build_dossier(tk, snaps, details, scores, signal_hits(tk, None, m3_tk, None), None, today)
                for tk in tickers}

    jobs = [(tk, m) for tk in tickers for m in MODELS]
    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(lambda j: analyst.analyze_stock_with_stats(dossiers[j[0]], model=j[1]), jobs))

    labels = MODELS[:]
    random.shuffle(labels)  # A/B 블라인드 배정
    by_model = {m: lab for lab, m in zip(["A", "B"], labels)}
    out = {
        "date": today,
        "labels": {"A": labels[0], "B": labels[1]},
        "stocks": [],
        "usage": analyst.usage_summary(),
    }
    for tk in tickers:
        entry = {"ticker": tk, "metrics": {k: v for k, v in dossiers[tk].items() if k != "holding"}, "runs": {}}
        for (jtk, m), (analysis, stats) in zip(jobs, results):
            if jtk == tk:
                entry["runs"][by_model[m]] = {"analysis": analysis, "stats": stats}
        out["stocks"].append(entry)

    os.makedirs(OUT_DIR, exist_ok=True)
    for name in ("latest.json", f"{today}.json"):
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
    for m, u in out["usage"].items():
        print(f"{m}: 호출 {u['calls']} · 입력 {u['input_tokens']:,} · 출력 {u['output_tokens']:,} · 검색 {u['web_searches']} · 추정 ${u['est_cost_usd']}")


if __name__ == "__main__":
    main()
