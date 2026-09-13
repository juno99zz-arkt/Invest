"""
주간 추천 후보 유니버스: S&P 500 + Nasdaq-100 (중복 제거).
수집 실패 시 data/universe.json 캐시(마지막 성공본)를 사용.
"""
import io
import json
import os
from datetime import datetime

import pandas as pd
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(BASE_DIR, "data", "universe.json")

SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
NDX_URL = "https://api.nasdaq.com/api/quote/list-type/nasdaq100"
BROWSER_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json,text/html"}


def _yahoo_symbol(sym):
    # BRK.B → BRK-B (yfinance 표기)
    return str(sym).strip().replace(".", "-")


def _fetch_sp500():
    r = requests.get(SP500_URL, headers=BROWSER_UA, timeout=30)
    r.raise_for_status()
    table = pd.read_html(io.StringIO(r.text))[0]
    return [(_yahoo_symbol(s), str(n)) for s, n in zip(table["Symbol"], table["Security"])]


def _fetch_ndx():
    r = requests.get(NDX_URL, headers=BROWSER_UA, timeout=30)
    r.raise_for_status()
    rows = r.json()["data"]["data"]["rows"]
    return [(_yahoo_symbol(row["symbol"]), row["companyName"]) for row in rows]


def load_universe():
    """[(ticker, name)] 반환."""
    try:
        merged = dict(_fetch_sp500())
        for sym, name in _fetch_ndx():
            merged.setdefault(sym, name)
        if len(merged) < 450:
            raise ValueError(f"유니버스 종목 수 비정상: {len(merged)}")
        tickers = sorted(merged.items())
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({"updated": datetime.now().strftime("%Y-%m-%d"), "tickers": tickers}, f, ensure_ascii=False, indent=0)
        print(f"유니버스 {len(tickers)}종목 수집")
        return tickers
    except Exception as e:
        print(f"경고: 유니버스 수집 실패({e}) — 캐시 사용")
        with open(CACHE_PATH, encoding="utf-8") as f:
            return [tuple(t) for t in json.load(f)["tickers"]]


if __name__ == "__main__":
    print(len(load_universe()))
