"""Claude 분석 전에 필요한 자료를 work/ 에 준비한다 (GitHub Actions 클라우드 분석용).

- work/context.json   : 오늘 날짜, 대시보드 경고(alerts), 공포·탐욕 단계·후보, 현재 보유 비중
- work/dossiers/TK.json : 요청서의 dossier 를 종목별 파일로 분리

예전에 Aside 가 대시보드 화면(INJECTED)에서 읽던 값을 generate_invest 의 같은 함수로 계산한다.
상위 50종목 시세 등 분석에 필요 없는 무거운 수집은 하지 않는다.
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fear as fear_mod  # noqa: E402
import generate_invest as gi  # noqa: E402

WORK = "work"


def main():
    os.makedirs(f"{WORK}/dossiers", exist_ok=True)
    with open("data/pending/request.json", encoding="utf-8") as f:
        req = json.load(f)

    weekly = gi._load("weekly_signals.json") or {}
    hist = gi._load("picks_history.json", {"portfolio": [], "closed": [], "weeks": []})
    report = gi._load(f"reports/{hist['weeks'][-1]['week'].split('+')[0]}.json") if hist.get("weeks") else None

    fg = fear_mod.load()
    fear_t = fear_mod.tier(fg)
    summary = gi.build_summary(weekly, hist, report)
    today = datetime.now(gi.KST).date().isoformat()
    fear_cands = gi._safe(lambda: gi.fear_candidates(report, hist, summary, fear_t), [])
    alerts = gi._safe(lambda: gi.build_alerts(hist, report, today), [])

    ctx = {
        "today": today,
        "weekday": datetime.now(gi.KST).strftime("%a"),
        "request_week": req.get("week"),
        "request_finalized_at": req.get("finalized_at"),
        "fear_greed": fg,
        "fear_tier": fear_t,
        "fear_candidates": fear_cands,
        "alerts": alerts,
        "holdings": hist.get("portfolio", []),
    }
    with open(f"{WORK}/context.json", "w", encoding="utf-8") as f:
        json.dump(ctx, f, ensure_ascii=False, indent=1, default=str)

    dossiers = req.get("dossiers") or []
    if isinstance(dossiers, dict):
        dossiers = [dict(v, ticker=v.get("ticker", k)) for k, v in dossiers.items()]
    for d in dossiers:
        with open(f"{WORK}/dossiers/{d['ticker']}.json", "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1, default=str)

    high = [a.get("ticker") for a in alerts if a.get("level") == "high"]
    print(f"오늘 {today} · 요청서 {req.get('week')} · to_analyze {[d.get('ticker') for d in req.get('to_analyze', [])]}")
    print(f"dossier {len(req.get('dossiers') or {})}개 · 경고(high) {high} · 공포·탐욕 단계 {fear_t.get('tier')}")


if __name__ == "__main__":
    main()
