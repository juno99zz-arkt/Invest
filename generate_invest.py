"""
매일 17:00 KST GitHub Actions에서 실행.
1. mock_data.py에서 데이터 로드
2. yfinance로 PEG 비율 실시간 갱신 (실패 시 mock 유지)
3. invest/index.html 생성 → gh-pages 커밋
"""
import json
import os
import sys

# 현재 스크립트 기준으로 investment-dashboard 모듈 경로 추가
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from mock_data import M1_DATA, M1_COMMON, M2_DATA, M3_DATA, M4_DATA, M5_DATA, M6_DATA, SUMMARY_DATA, NEWS_DATA

# ── PEG 실시간 업데이트 ─────────────────────────────────────────
PEG_TICKERS = [
    ("PLTR","Palantir"), ("TSLA","Tesla"),   ("NVDA","Nvidia"),
    ("AAPL","Apple"),    ("MSFT","Microsoft"),("APP","Applovin"),
    ("META","Meta"),     ("AVGO","Broadcom"), ("AMZN","Amazon"), ("GOOGL","Alphabet"),
]
INDEX_TICKERS = [
    ("SPY",  "S&P 500 (SPY)"),
    ("QQQ",  "나스닥 100 (QQQ)"),
    ("SOXX", "반도체 섹터 (SOXX)"),
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
                    result.append({
                        "ticker": ticker, "name": name,
                        "peg": round(float(peg), 1),
                        "pe":  round(float(pe),  1),
                        "growth_rate": round(float(pe) / float(peg), 1),
                    })
            except Exception:
                pass
        result.sort(key=lambda x: x["peg"], reverse=True)
        return result or None
    except ImportError:
        return None

def fetch_index_peg():
    try:
        import yfinance as yf
        result = []
        for ticker, name in INDEX_TICKERS:
            try:
                info = yf.Ticker(ticker).info
                peg = info.get("trailingPegRatio") or info.get("pegRatio")
                pe  = info.get("trailingPE") or info.get("forwardPE")
                if pe:
                    entry = {"ticker": ticker, "name": name, "pe": round(float(pe), 1)}
                    if peg:
                        entry["peg"] = round(float(peg), 1)
                        entry["growth_rate"] = round(float(pe) / float(peg), 1)
                    else:
                        entry["peg"] = None
                        entry["growth_rate"] = None
                    result.append(entry)
            except Exception:
                pass
        return result or None
    except ImportError:
        return None

# ── 데이터 조합 ─────────────────────────────────────────────────
def build_data():
    peg = fetch_peg()
    if peg:
        M6_DATA["peg_ratios"] = peg
        print(f"PEG 실시간 데이터 {len(peg)}개 반영")
    else:
        print("yfinance 없음 — mock PEG 사용")
    idx_peg = fetch_index_peg()
    if idx_peg:
        M6_DATA["index_peg"] = idx_peg
        print(f"지수 PEG 실시간 데이터 {len(idx_peg)}개 반영")

    return {
        "summary": SUMMARY_DATA,
        "news": NEWS_DATA,
        "m1": {"investors": M1_DATA, "common_top3": M1_COMMON},
        "m2": {"sectors": M2_DATA},
        "m3": {"companies": M3_DATA},
        "m4": {"companies": M4_DATA},
        "m5": M5_DATA,
        "m6": M6_DATA,
    }

def inject_data(html, data_json):
    lines = html.split('\n')
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if start_idx is None and stripped.startswith('const INJECTED ='):
            start_idx = i
            if stripped.endswith(';'):
                end_idx = i
                break
        elif start_idx is not None and stripped == '};':
            end_idx = i
            break
    if start_idx is not None and end_idx is not None:
        html = '\n'.join(lines[:start_idx] + ['const INJECTED = ' + data_json + ';'] + lines[end_idx+1:])
        print(f"INJECTED 교체 성공 (line {start_idx}~{end_idx})")
    else:
        print(f"경고: INJECTED 블록 찾기 실패 (start={start_idx}, end={end_idx})")
    return html

# ── HTML 생성 ───────────────────────────────────────────────────
def generate():
    data = build_data()
    data_json = json.dumps(data, ensure_ascii=False)

    html_path = os.path.join(BASE_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    html = inject_data(html, data_json)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"생성 완료: {html_path}")

if __name__ == "__main__":
    generate()
