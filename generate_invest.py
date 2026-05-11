import json, os, sys, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from mock_data import M1_DATA, M1_COMMON, M2_DATA, M3_DATA, M4_DATA, M5_DATA, M6_DATA, SUMMARY_DATA

PEG_TICKERS = [
    ("PLTR","Palantir"),("TSLA","Tesla"),("NVDA","Nvidia"),
    ("AAPL","Apple"),("MSFT","Microsoft"),("APP","Applovin"),
    ("META","Meta"),("AVGO","Broadcom"),("AMZN","Amazon"),("GOOGL","Alphabet"),
]

def fetch_peg():
    try:
        import yfinance as yf
        result = []
        for ticker, name in PEG_TICKERS:
            try:
                info = yf.Ticker(ticker).info
                peg = info.get("trailingPegRatio") or info.get("pegRatio")
                pe  = info.get("trailingPE") or info.get("forwardPE")
                if peg and pe:
                    result.append({"ticker":ticker,"name":name,
                        "peg":round(float(peg),1),"pe":round(float(pe),1),
                        "growth_rate":round(float(pe)/float(peg),1)})
            except: pass
        result.sort(key=lambda x: x["peg"], reverse=True)
        return result or None
    except ImportError:
        return None

def build_data():
    peg = fetch_peg()
    if peg:
        M6_DATA["peg_ratios"] = peg
        print(f"PEG 실시간 {len(peg)}개 반영")
    return {
        "summary": SUMMARY_DATA,
        "m1": {"investors": M1_DATA, "common_top3": M1_COMMON},
        "m2": {"sectors": M2_DATA},
        "m3": {"companies": M3_DATA},
        "m4": {"companies": M4_DATA},
        "m5": M5_DATA,
        "m6": M6_DATA,
    }

def generate():
    data = build_data()
    data_json = json.dumps(data, ensure_ascii=False)

    html_path = os.path.join(BASE_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # INJECTED 블록을 최신 데이터로 교체
    new_block = "const INJECTED = " + data_json + ";"
    html = re.sub(r"const INJECTED = \{[\s\S]*?\};", new_block, html)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"완료: {html_path}")

if __name__ == "__main__":
    generate()

