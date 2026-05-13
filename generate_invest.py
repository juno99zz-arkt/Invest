"""
매일 17:00 KST GitHub Actions에서 실행.
1. mock_data.py에서 데이터 로드
2. yfinance로 실시간 갱신:
   - M6 PEG (30종목)
   - M7 시총 상위 50 × 5지표 + 신호등
   - M4 흑자전환 현재가 → 추정 PER 계산
3. 빌드 메타(KST 타임스탬프) 주입
4. index.html INJECTED 교체 → gh-pages 커밋
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

# 현재 스크립트 기준으로 investment-dashboard 모듈 경로 추가
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from mock_data import M1_DATA, M1_COMMON, M2_DATA, M3_DATA, M4_DATA, M5_DATA, M6_DATA, M7_DATA, SUMMARY_DATA, NEWS_DATA
from data_fetcher import PEG_TICKERS, fetch_top50_metrics, fetch_prices

KST = timezone(timedelta(hours=9))

# ── PEG 실시간 업데이트 (티커 정의는 data_fetcher.PEG_TICKERS 단일 소스) ────
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

# ── M4 추정 PER 계산 ────────────────────────────────────────────
def _signal_pe(pe):
    if pe is None: return "gray"
    if pe < 15: return "green"
    if pe <= 25: return "yellow"
    return "red"

def update_m4_projected_pe():
    """yfinance 현재가 fetch → projected_pe = current_price ÷ (consensus_eps × 4)."""
    tickers = [c["ticker"] for c in M4_DATA]
    prices = fetch_prices(tickers)
    if not prices:
        # 신호등만 mock 값 기준으로 채움
        for c in M4_DATA:
            c["sig_proj_pe"] = _signal_pe(c.get("projected_pe"))
        print("yfinance 없음 — M4 mock 현재가 사용")
        return
    for c in M4_DATA:
        price = prices.get(c["ticker"])
        if price and c.get("consensus_eps", 0) > 0:
            # consensus_eps 는 분기 EPS → 연환산 (4분기 가정)
            projected_eps_annual = c["consensus_eps"] * 4
            c["current_price"] = round(price, 2)
            c["projected_pe"]  = round(price / projected_eps_annual, 1)
        c["sig_proj_pe"] = _signal_pe(c.get("projected_pe"))
    print(f"M4 현재가 {len(prices)}개 갱신 + 추정 PER 계산 완료")

# ── 데이터 조합 ─────────────────────────────────────────────────
def build_data():
    peg = fetch_peg()
    if peg:
        M6_DATA["peg_ratios"] = peg
        print(f"PEG 실시간 데이터 {len(peg)}개 반영")
    else:
        print("yfinance 없음 — mock PEG 사용")
    M6_DATA.pop("index_peg", None)

    # M7 시총 상위 50 × 5지표
    top50 = fetch_top50_metrics()
    if top50:
        M7_DATA["stocks"] = top50
        print(f"M7 상위 50종목 {len(top50)}개 실시간 갱신")
    else:
        print("yfinance 없음 — M7 mock 사용")

    # M4 현재가 + 추정 PER
    update_m4_projected_pe()

    # 빌드 시각 (KST)
    now_kst = datetime.now(KST)
    build_meta = {
        "built_at_kst":   now_kst.strftime("%Y-%m-%d %H:%M"),
        "built_at_iso":   now_kst.isoformat(),
        "schedule_label": "매일 KST 17:00 자동 갱신",
    }

    return {
        "summary": SUMMARY_DATA,
        "news": NEWS_DATA,
        "m1": {"investors": M1_DATA, "common_top3": M1_COMMON},
        "m2": {"sectors": M2_DATA},
        "m3": {"companies": M3_DATA},
        "m4": {"companies": M4_DATA},
        "m5": M5_DATA,
        "m6": M6_DATA,
        "m7": M7_DATA,
        "meta": build_meta,
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
