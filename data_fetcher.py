"""
매일 17:00 KST 실행되는 데이터 업데이트 모듈.
현재: yfinance로 PEG Ratio 실시간 갱신.
추후: SEC EDGAR 13F, 내부자 거래 자동화 확장 가능.
"""

# 미국 시총 상위 20 + 전세계 반도체 상위 10 (NVDA·AVGO 중복 제외) = 30종목
PEG_TICKERS = [
    # ── US market cap top 20 ──
    ("AAPL",      "Apple"),
    ("MSFT",      "Microsoft"),
    ("NVDA",      "Nvidia"),
    ("GOOGL",     "Alphabet"),
    ("AMZN",      "Amazon"),
    ("META",      "Meta"),
    ("TSLA",      "Tesla"),
    ("BRK-B",     "Berkshire"),
    ("AVGO",      "Broadcom"),
    ("WMT",       "Walmart"),
    ("JPM",       "JPMorgan"),
    ("ORCL",      "Oracle"),
    ("LLY",       "Eli Lilly"),
    ("V",         "Visa"),
    ("MA",        "Mastercard"),
    ("NFLX",      "Netflix"),
    ("XOM",       "ExxonMobil"),
    ("COST",      "Costco"),
    ("JNJ",       "Johnson & Johnson"),
    ("HD",        "Home Depot"),
    # ── Global semiconductor top 10 (NVDA·AVGO 제외) ──
    ("TSM",       "TSMC"),
    ("ASML",      "ASML"),
    ("AMD",       "AMD"),
    ("QCOM",      "Qualcomm"),
    ("TXN",       "Texas Instruments"),
    ("ARM",       "ARM Holdings"),
    ("MU",        "Micron"),
    ("AMAT",      "Applied Materials"),
    ("005930.KS", "삼성전자"),
    ("000660.KS", "SK하이닉스"),
]

def fetch_peg_ratios():
    """yfinance로 PEG 비율 가져오기. 실패 시 이전 값 유지."""
    try:
        import yfinance as yf
        result = []
        for ticker, name in PEG_TICKERS:
            try:
                info = yf.Ticker(ticker).info
                peg  = info.get("trailingPegRatio") or info.get("pegRatio")
                pe   = info.get("trailingPE") or info.get("forwardPE")
                if peg and pe:
                    result.append({
                        "ticker": ticker,
                        "name": name,
                        "peg": round(float(peg), 1),
                        "pe":  round(float(pe), 1),
                        "growth_rate": round(float(pe) / float(peg), 1) if peg else 0,
                    })
            except Exception:
                pass
        result.sort(key=lambda x: x["peg"], reverse=True)
        return result if result else None
    except ImportError:
        return None

def fetch_and_update(m6_data: dict):
    """M6_DATA의 peg_ratios를 실시간 값으로 교체."""
    peg = fetch_peg_ratios()
    if peg:
        m6_data["peg_ratios"] = peg

if __name__ == "__main__":
    data = fetch_peg_ratios()
    if data:
        for d in data:
            flag = " ⚠️" if d["peg"] >= 1.5 else ""
            print(f"{d['ticker']:6s} PEG={d['peg']}  PE={d['pe']}{flag}")
    else:
        print("yfinance 미설치 또는 API 오류")
