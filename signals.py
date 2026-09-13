"""
수집한 원자료 → 대시보드 섹션(M2 섹터 / M3 실적개선 / M4 흑자전환 / M6 사이클) 구성.
M1(13F)·M5(Form 4)는 sec_data 결과를 그대로 사용.
"""
from statistics import median

SECTOR_KR = {
    "Technology": "IT·기술", "Communication Services": "커뮤니케이션", "Financial Services": "금융",
    "Healthcare": "헬스케어", "Consumer Cyclical": "경기소비재", "Consumer Defensive": "필수소비재",
    "Energy": "에너지", "Industrials": "산업재", "Basic Materials": "소재",
    "Real Estate": "부동산", "Utilities": "유틸리티",
}

SEMI_TICKERS = ["NVDA", "AVGO", "AMD", "TSM", "ASML", "MU", "QCOM", "AMAT"]
CAPEX_TICKERS = ["MSFT", "GOOGL", "AMZN", "META", "ORCL"]


def _r(v, n=1):
    return None if v is None else round(v, n)


def build_m2(snaps):
    """섹터별 다음 회계연도 EPS 컨센서스 30일 변화(중앙값) + 상향 비율."""
    groups = {}
    for s in snaps.values():
        if s.get("rev_30d") is not None and s["sector"] in SECTOR_KR:
            groups.setdefault(s["sector"], []).append(s)
    sectors = []
    for sector, rows in groups.items():
        rev30 = median(r["rev_30d"] for r in rows)
        up = sum(r.get("up_30d") or 0 for r in rows)
        down = sum(r.get("down_30d") or 0 for r in rows)
        path = []
        for i in range(5):
            vals = [r["rev_path"][i] for r in rows if r.get("rev_path") and r["rev_path"][i] is not None]
            path.append(_r(median(vals), 2) if vals else 0)
        sectors.append({
            "sector": sector, "sector_kr": SECTOR_KR[sector], "stocks": len(rows),
            "eps_revision_pct_30d": _r(rev30, 2),
            "eps_revision_pct_7d": _r(median(r["rev_7d"] for r in rows if r.get("rev_7d") is not None), 2),
            "upgrade_ratio": round(up / (up + down), 2) if up + down else None,
            "momentum": "↑상승중" if rev30 >= 0.5 else "↓하락중" if rev30 <= -0.5 else "→횡보",
            "sparkline": path,
        })
    sectors.sort(key=lambda x: -x["eps_revision_pct_30d"])
    return {"sectors": sectors}


def build_m3(snaps, limit=10):
    """실적 개선 기업: 최근 분기 매출·EPS 성장 + 추정치 상향이 동시에 나타나는 종목."""
    rows = []
    for s in snaps.values():
        rg, eg, r30, r90 = s.get("revenue_growth"), s.get("earnings_growth"), s.get("rev_30d"), s.get("rev_90d")
        up, down = s.get("up_30d") or 0, s.get("down_30d") or 0
        if None in (rg, eg, r30, r90):
            continue
        if rg >= 0.10 and eg >= 0.15 and r30 > 0 and r90 > 0 and up > down and (s.get("analysts") or 0) >= 5:
            score = min(rg, 1.0) * 40 + min(eg, 2.0) * 20 + min(r90, 30) * 1.5 + min(r30, 15) * 1.0
            rows.append((score, s))
    rows.sort(key=lambda x: -x[0])
    return [s["ticker"] for _, s in rows[:limit]]


def m3_section(tickers, snaps, details):
    companies = []
    for rank, tk in enumerate(tickers, 1):
        s, d = snaps[tk], details.get(tk, {})
        companies.append({
            "rank": rank, "ticker": tk, "name": s["name"],
            "sector": SECTOR_KR.get(s["sector"], s["sector"]),
            "market_cap_b": round(s["market_cap"] / 1e9),
            "revenue_growth_pct": _r(s["revenue_growth"] * 100),
            "earnings_growth_pct": _r(s["earnings_growth"] * 100),
            "eps_revision_30d": _r(s["rev_30d"], 2), "eps_revision_90d": _r(s["rev_90d"], 2),
            "up_30d": s.get("up_30d"), "down_30d": s.get("down_30d"),
            "op_margin_q": [v for _, v in d.get("q_op_margin", [])],
            "eps_surprises": [x["surprise_pct"] for x in d.get("eps_surprises", [])],
            "next_earnings": d.get("next_earnings"),
        })
    return {"companies": companies}


def build_m4(snaps, limit=25):
    """흑자전환 1차 후보: 최근 12개월 EPS 적자 + 향후 12개월 추정 EPS 흑자 + 애널리스트 3인 이상.
    일회성 손실 걸러내기는 상세 데이터(조정 EPS) 수집 후 m4_section 에서."""
    rows = [s for s in snaps.values()
            if (s.get("trailing_eps") or 0) < 0 and (s.get("forward_eps") or 0) > 0 and (s.get("analysts") or 0) >= 3]
    rows.sort(key=lambda s: -s["market_cap"])
    return [s["ticker"] for s in rows[:limit]]


def _signal_pe(pe):
    if pe is None: return "gray"
    if pe < 15: return "green"
    if pe <= 25: return "yellow"
    return "red"


def m4_section(tickers, snaps, details, limit=10):
    """회계상 일회성 손실(손상차손 등)로만 적자인 기업 제외: 최근 2분기 조정 EPS 중 적자가 있어야 함."""
    real = [tk for tk in tickers
            if any(x["actual"] is not None and x["actual"] < 0
                   for x in details.get(tk, {}).get("eps_surprises", [])[-2:])]
    companies = []
    for rank, tk in enumerate(real[:limit], 1):
        s, d = snaps[tk], details.get(tk, {})
        if (s.get("eps_0q") or 0) > 0:
            when = "이번 분기 흑자 예상"
        elif (s.get("eps_1q") or 0) > 0:
            when = "다음 분기 흑자 예상"
        elif (s.get("eps_0y") or 0) > 0:
            when = "올해 연간 흑자 예상"
        else:
            when = "내년 연간 흑자 예상"
        ppe = s["price"] / s["forward_eps"] if s.get("price") else None
        companies.append({
            "rank": rank, "ticker": tk, "name": s["name"], "market_cap_b": round(s["market_cap"] / 1e9, 1),
            "turnaround_quarter": when, "trailing_eps": _r(s["trailing_eps"], 2),
            "consensus_eps": _r(s["forward_eps"], 2), "analyst_count": int(s.get("analysts") or 0),
            "current_price": _r(s.get("price"), 2), "projected_pe": _r(ppe),
            "sig_proj_pe": _signal_pe(ppe),
            "recent_eps": [x["actual"] for x in d.get("eps_surprises", [])][-2:],
        })
    return {"companies": companies}


def build_m6(snaps, details):
    semis = []
    for tk in SEMI_TICKERS:
        s = snaps.get(tk)
        if not s:
            continue
        g0, g1 = s.get("growth_0y"), s.get("growth_1y")
        if g0 is None or g1 is None:
            trend = "데이터 부족"
        elif g1 < 0:
            trend = "역성장 전망"
        elif g1 < g0 * 0.7:
            trend = "둔화 전망"
        elif g1 > g0:
            trend = "가속 전망"
        else:
            trend = "지속 성장"
        semis.append({
            "ticker": tk,
            "eps_growth_last_q": _r((s.get("earnings_growth") or 0) * 100) if s.get("earnings_growth") is not None else None,
            "eps_growth_this_fy": _r(g0 * 100) if g0 is not None else None,
            "eps_growth_next_fy": _r(g1 * 100) if g1 is not None else None,
            "trend": trend,
        })

    capex = []
    for tk in CAPEX_TICKERS:
        q = [(p, v) for p, v in details.get(tk, {}).get("q_capex", []) if v is not None]
        if len(q) < 2:
            continue
        yoy = _r((q[-1][1] - q[0][1]) / q[0][1] * 100) if len(q) == 5 and q[0][1] else None
        capex.append({"ticker": tk, "capex_q_b": [round(v / 1e9, 1) for _, v in q],
                      "quarters": [p for p, _ in q], "yoy_growth_pct": yoy})

    slow = sum(1 for x in semis if x["trend"] in ("둔화 전망", "역성장 전망"))
    yoys = [c["yoy_growth_pct"] for c in capex if c["yoy_growth_pct"] is not None]
    capex_med = median(yoys) if yoys else None
    semi_trend = "둔화 전망 우세" if slow > len(semis) / 2 else "성장 지속"
    capex_trend = "데이터 부족" if capex_med is None else "확대" if capex_med >= 20 else "유지" if capex_med >= 0 else "축소"
    if capex_trend == "축소" or (slow > len(semis) / 2 and capex_trend != "확대"):
        signal = "경계"
    elif capex_trend == "확대" and slow <= len(semis) / 3:
        signal = "지속"
    else:
        signal = "주의"
    summary = (f"반도체 {len(semis)}종목 중 {slow}종목이 내년 EPS 성장 둔화·역성장 전망. "
               + (f"빅테크 {len(yoys)}사 분기 CapEx 전년동기 대비 중앙값 {capex_med:+.0f}%." if capex_med is not None else "CapEx 데이터 부족.")
               + " (컨센서스·재무공시 기반 자동 판정)")
    return {
        "semiconductor": semis, "capex": capex,
        "overall": {"semiconductor_growth_trend": semi_trend, "capex_trend": capex_trend,
                    "bull_market_signal": signal, "summary": summary},
    }
