"""
매일 17:00 KST 실행되는 데이터 업데이트 모듈.
- PEG_TICKERS : M6 PEG 과열 모니터 (30종목)
- TOP50_TICKERS : M7 시총 상위 50종목 5지표 + 신호등
- M4 흑자전환 종목 추정 PER 계산용 현재가 fetch
"""

# 미국 시총 상위 50종목 (대형주 기준, yfinance 호환 티커)
TOP50_TICKERS = [
    ("AAPL",  "Apple"),
    ("MSFT",  "Microsoft"),
    ("NVDA",  "Nvidia"),
    ("GOOGL", "Alphabet"),
    ("AMZN",  "Amazon"),
    ("META",  "Meta"),
    ("TSLA",  "Tesla"),
    ("BRK-B", "Berkshire"),
    ("AVGO",  "Broadcom"),
    ("WMT",   "Walmart"),
    ("JPM",   "JPMorgan"),
    ("ORCL",  "Oracle"),
    ("LLY",   "Eli Lilly"),
    ("V",     "Visa"),
    ("MA",    "Mastercard"),
    ("NFLX",  "Netflix"),
    ("XOM",   "ExxonMobil"),
    ("COST",  "Costco"),
    ("JNJ",   "Johnson & Johnson"),
    ("HD",    "Home Depot"),
    ("PG",    "P&G"),
    ("BAC",   "Bank of America"),
    ("ABBV",  "AbbVie"),
    ("KO",    "Coca-Cola"),
    ("CVX",   "Chevron"),
    ("CRM",   "Salesforce"),
    ("AMD",   "AMD"),
    ("MRK",   "Merck"),
    ("TMO",   "Thermo Fisher"),
    ("PEP",   "PepsiCo"),
    ("ACN",   "Accenture"),
    ("ADBE",  "Adobe"),
    ("LIN",   "Linde"),
    ("MCD",   "McDonald's"),
    ("CSCO",  "Cisco"),
    ("ABT",   "Abbott"),
    ("IBM",   "IBM"),
    ("GE",    "GE Aerospace"),
    ("NOW",   "ServiceNow"),
    ("AXP",   "American Express"),
    ("PM",    "Philip Morris"),
    ("DIS",   "Disney"),
    ("INTU",  "Intuit"),
    ("T",     "AT&T"),
    ("MS",    "Morgan Stanley"),
    ("ISRG",  "Intuitive Surgical"),
    ("CAT",   "Caterpillar"),
    ("GS",    "Goldman Sachs"),
    ("VZ",    "Verizon"),
    ("RTX",   "RTX"),
]

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

def _signal_pe(pe):
    """PER 신호등: <15 녹 / 15-25 주 / >25 빨."""
    if pe is None: return "gray"
    if pe < 15: return "green"
    if pe <= 25: return "yellow"
    return "red"

def _signal_peg(peg):
    """PEG 신호등: <1 녹 / 1-1.5 주 / >1.5 빨."""
    if peg is None: return "gray"
    if peg < 1.0: return "green"
    if peg <= 1.5: return "yellow"
    return "red"

def _signal_growth(g):
    """매출·EPS 성장률 신호등 (%): >15 녹 / 5-15 주 / <5 빨."""
    if g is None: return "gray"
    if g > 15: return "green"
    if g >= 5: return "yellow"
    return "red"

def _signal_trend(arrow):
    """EPS 추이 신호등: ↑ 녹 / → 주 / ↓ 빨."""
    return {"↑": "green", "→": "yellow", "↓": "red"}.get(arrow, "gray")


def fetch_top50_metrics():
    """시총 상위 50종목 × (PER · PEG · 매출성장 · EPS성장 · EPS추이) + 신호등."""
    try:
        import yfinance as yf
        result = []
        for ticker, name in TOP50_TICKERS:
            try:
                info = yf.Ticker(ticker).info
                pe  = info.get("trailingPE") or info.get("forwardPE")
                peg = info.get("trailingPegRatio") or info.get("pegRatio")
                rev = info.get("revenueGrowth")     # 분수
                eps = info.get("earningsGrowth")    # 분수
                fwd_eps   = info.get("forwardEps")
                trail_eps = info.get("trailingEps")

                # EPS 컨센서스 추이: forwardEps vs trailingEps
                if fwd_eps is not None and trail_eps is not None and trail_eps != 0:
                    delta = (fwd_eps - trail_eps) / abs(trail_eps)
                    if delta > 0.05:  arrow = "↑"
                    elif delta < -0.05: arrow = "↓"
                    else: arrow = "→"
                else:
                    arrow = "→"

                rev_pct = round(rev * 100, 1) if rev is not None else None
                eps_pct = round(eps * 100, 1) if eps is not None else None
                pe_r  = round(float(pe), 1) if pe else None
                peg_r = round(float(peg), 1) if peg else None

                result.append({
                    "ticker": ticker,
                    "name": name,
                    "pe": pe_r,
                    "peg": peg_r,
                    "rev_growth": rev_pct,
                    "eps_growth": eps_pct,
                    "eps_trend": arrow,
                    "sig_pe":     _signal_pe(pe_r),
                    "sig_peg":    _signal_peg(peg_r),
                    "sig_rev":    _signal_growth(rev_pct),
                    "sig_eps":    _signal_growth(eps_pct),
                    "sig_trend":  _signal_trend(arrow),
                })
            except Exception:
                pass
        return result or None
    except ImportError:
        return None


def fetch_prices(tickers):
    """현재가 dict 반환 — M4 추정 PER 계산용."""
    try:
        import yfinance as yf
        out = {}
        for t in tickers:
            try:
                info = yf.Ticker(t).info
                price = info.get("currentPrice") or info.get("regularMarketPrice")
                if price:
                    out[t] = float(price)
            except Exception:
                pass
        return out
    except ImportError:
        return {}


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
