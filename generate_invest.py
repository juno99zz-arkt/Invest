"""Build a dated US equity research dashboard for GitHub Pages."""
import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from data_fetcher import TOP50_TICKERS, fetch_research_stocks, fetch_research_news
from research_engine import MODEL, score_stocks, select_week, report

BASE_DIR = Path(__file__).resolve().parent
KST = timezone(timedelta(hours=9))


def build_data(now, previous=None, tickers=None):
    universe = tickers if tickers is not None else TOP50_TICKERS
    stocks, errors = fetch_research_stocks(universe, now)
    ranked = score_stocks(stocks, now)
    dated = [s for s in ranked if not any("시점" in x or "기준일" in x or "실제 수집" in x for x in s["excluded"])]
    healthy = len(dated) >= max(1, int(len(universe) * .8 + .999))
    history = (previous or {}).get("history", [])
    if healthy:
        history = select_week(ranked, history, now)
    latest = history[-1] if history else None
    selected = {s["ticker"] for s in latest["picks"]} if latest else set()
    for s in ranked:
        s["report"] = report(s)
        s["news"] = []
        if s["ticker"] in selected:
            try:
                s["news"] = fetch_research_news(s["ticker"], now)
            except Exception as exc:
                errors.append(dict(ticker=s["ticker"], stage="뉴스", error=type(exc).__name__))
    return dict(meta=dict(built_at=now.isoformat(), model=MODEL, healthy=healthy,
                          universe_size=len(universe), fetched=len(stocks), dated=len(dated),
                          schedule="매일 17:00 KST 수집 · 매주 첫 정상 실행에 선정", horizon="6개월 이상"),
                stocks=ranked, history=history, errors=errors)


def render_html(data):
    template = (BASE_DIR / "index.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    if template.count("/*__DATA__*/null") != 1:
        raise ValueError("Dashboard data marker missing or duplicated")
    return template.replace("/*__DATA__*/null", payload)


def generate():
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", type=Path, default=BASE_DIR / "dist")
    parser.add_argument("--tickers", help="Comma-separated subset for live smoke testing")
    args = parser.parse_args()
    previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous and args.previous.exists() else None
    tickers = [(x.strip(), x.strip()) for x in args.tickers.split(",")] if args.tickers else None
    data = build_data(datetime.now(KST), previous, tickers)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "index.html").write_text(render_html(data), encoding="utf-8")
    (args.output / "research.json").write_text(json.dumps(data, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    (args.output / ".nojekyll").touch()
    print(f"생성 완료: {args.output}; 정상 수집={data['meta']['healthy']}")


if __name__ == "__main__":
    generate()
