from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")

# ── M1 대가의 포트폴리오 ──────────────────────────────────────────
M1_DATA = [
    {
        "investor": "Warren Buffett",
        "firm": "Berkshire Hathaway",
        "filed_date": "2025-02-14",
        "top10": [
            {"ticker": "AAPL", "name": "Apple", "weight_pct": 28.4, "change": -2.1, "flag": "감소"},
            {"ticker": "BAC",  "name": "Bank of America", "weight_pct": 11.2, "change": 0.0, "flag": "유지"},
            {"ticker": "AXP",  "name": "American Express", "weight_pct": 8.9, "change": +0.3, "flag": "증가"},
            {"ticker": "KO",   "name": "Coca-Cola", "weight_pct": 8.3, "change": 0.0, "flag": "유지"},
            {"ticker": "CVX",  "name": "Chevron", "weight_pct": 6.1, "change": -0.8, "flag": "감소"},
            {"ticker": "OXY",  "name": "Occidental Petroleum", "weight_pct": 5.4, "change": +0.2, "flag": "증가"},
            {"ticker": "MCO",  "name": "Moody's", "weight_pct": 4.8, "change": 0.0, "flag": "유지"},
            {"ticker": "KHC",  "name": "Kraft Heinz", "weight_pct": 4.1, "change": 0.0, "flag": "유지"},
            {"ticker": "DVA",  "name": "DaVita", "weight_pct": 2.9, "change": +0.4, "flag": "증가"},
            {"ticker": "VRSN", "name": "VeriSign", "weight_pct": 2.1, "change": 0.0, "flag": "유지"},
        ],
        "new_positions": [],
        "exited_positions": ["HP Inc", "Paramount Global"],
    },
    {
        "investor": "Bill Ackman",
        "firm": "Pershing Square",
        "filed_date": "2025-02-14",
        "top10": [
            {"ticker": "HHH",  "name": "Howard Hughes", "weight_pct": 22.1, "change": +1.2, "flag": "증가"},
            {"ticker": "QSR",  "name": "Restaurant Brands", "weight_pct": 18.7, "change": 0.0, "flag": "유지"},
            {"ticker": "GOOGL","name": "Alphabet", "weight_pct": 15.3, "change": +3.1, "flag": "증가"},
            {"ticker": "CMG",  "name": "Chipotle", "weight_pct": 14.2, "change": -1.0, "flag": "감소"},
            {"ticker": "CP",   "name": "Canadian Pacific", "weight_pct": 11.8, "change": 0.0, "flag": "유지"},
            {"ticker": "HLT",  "name": "Hilton", "weight_pct": 9.4, "change": +0.5, "flag": "증가"},
            {"ticker": "BN",   "name": "Brookfield", "weight_pct": 5.2, "change": 0.0, "flag": "유지"},
            {"ticker": "UNI",  "name": "Universal Music", "weight_pct": 3.3, "change": "NEW", "flag": "신규"},
        ],
        "new_positions": ["UNI"],
        "exited_positions": [],
    },
    {
        "investor": "Cathie Wood",
        "firm": "ARK Invest",
        "filed_date": "2025-02-14",
        "top10": [
            {"ticker": "TSLA", "name": "Tesla", "weight_pct": 14.2, "change": +1.8, "flag": "증가"},
            {"ticker": "COIN", "name": "Coinbase", "weight_pct": 9.1, "change": +2.3, "flag": "증가"},
            {"ticker": "ROKU", "name": "Roku", "weight_pct": 7.8, "change": -0.5, "flag": "감소"},
            {"ticker": "PLTR", "name": "Palantir", "weight_pct": 6.9, "change": +1.1, "flag": "증가"},
            {"ticker": "EXAS", "name": "Exact Sciences", "weight_pct": 5.4, "change": 0.0, "flag": "유지"},
            {"ticker": "PATH", "name": "UiPath", "weight_pct": 4.8, "change": -0.3, "flag": "감소"},
            {"ticker": "CRSP", "name": "CRISPR Therapeutics", "weight_pct": 4.1, "change": 0.0, "flag": "유지"},
            {"ticker": "HOOD", "name": "Robinhood", "weight_pct": 3.9, "change": "NEW", "flag": "신규"},
            {"ticker": "SQ",   "name": "Block", "weight_pct": 3.6, "change": -0.2, "flag": "감소"},
            {"ticker": "NVDA", "name": "Nvidia", "weight_pct": 3.2, "change": +0.7, "flag": "증가"},
        ],
        "new_positions": ["HOOD"],
        "exited_positions": ["ZM"],
    },
    {
        "investor": "Stan Druckenmiller",
        "firm": "Duquesne",
        "filed_date": "2025-02-14",
        "top10": [
            {"ticker": "NVDA", "name": "Nvidia", "weight_pct": 18.9, "change": +4.2, "flag": "증가"},
            {"ticker": "MSFT", "name": "Microsoft", "weight_pct": 12.3, "change": -1.5, "flag": "감소"},
            {"ticker": "META", "name": "Meta", "weight_pct": 10.8, "change": +2.1, "flag": "증가"},
            {"ticker": "AMZN", "name": "Amazon", "weight_pct": 9.4, "change": +0.8, "flag": "증가"},
            {"ticker": "GE",   "name": "GE Aerospace", "weight_pct": 7.2, "change": "NEW", "flag": "신규"},
            {"ticker": "NVO",  "name": "Novo Nordisk", "weight_pct": 6.1, "change": -2.0, "flag": "감소"},
            {"ticker": "PANW", "name": "Palo Alto Networks", "weight_pct": 5.3, "change": +0.4, "flag": "증가"},
            {"ticker": "APP",  "name": "Applovin", "weight_pct": 4.8, "change": "NEW", "flag": "신규"},
            {"ticker": "CRWD", "name": "CrowdStrike", "weight_pct": 3.9, "change": 0.0, "flag": "유지"},
            {"ticker": "AXON", "name": "Axon Enterprise", "weight_pct": 3.1, "change": +0.6, "flag": "증가"},
        ],
        "new_positions": ["GE", "APP"],
        "exited_positions": ["LLY"],
    },
    {
        "investor": "Chase Coleman",
        "firm": "Tiger Global",
        "filed_date": "2025-02-14",
        "top10": [
            {"ticker": "MSFT", "name": "Microsoft", "weight_pct": 16.4, "change": +1.0, "flag": "증가"},
            {"ticker": "NVDA", "name": "Nvidia", "weight_pct": 13.7, "change": +3.5, "flag": "증가"},
            {"ticker": "META", "name": "Meta", "weight_pct": 11.2, "change": +2.8, "flag": "증가"},
            {"ticker": "AMZN", "name": "Amazon", "weight_pct": 10.1, "change": 0.0, "flag": "유지"},
            {"ticker": "GOOGL","name": "Alphabet", "weight_pct": 8.9, "change": +1.3, "flag": "증가"},
            {"ticker": "ADBE", "name": "Adobe", "weight_pct": 5.6, "change": -0.7, "flag": "감소"},
            {"ticker": "CRM",  "name": "Salesforce", "weight_pct": 4.8, "change": 0.0, "flag": "유지"},
            {"ticker": "NOW",  "name": "ServiceNow", "weight_pct": 4.2, "change": +0.9, "flag": "증가"},
            {"ticker": "SNOW", "name": "Snowflake", "weight_pct": 3.5, "change": -1.2, "flag": "감소"},
            {"ticker": "DDOG", "name": "Datadog", "weight_pct": 2.9, "change": "NEW", "flag": "신규"},
        ],
        "new_positions": ["DDOG"],
        "exited_positions": ["SHOP"],
    },
]
M1_COMMON = ["NVDA", "MSFT", "META"]

# ── M2 실적 개선 섹터 ──────────────────────────────────────────────
M2_DATA = [
    {"sector": "Information Technology", "sector_kr": "IT·기술", "eps_revision_pct_week": 1.8, "upgrade_ratio": 0.72, "momentum": "↑상승중", "sparkline": [0.2, 0.4, 0.5, 0.8, 1.8]},
    {"sector": "Communication Services", "sector_kr": "커뮤니케이션", "eps_revision_pct_week": 1.4, "upgrade_ratio": 0.68, "momentum": "↑상승중", "sparkline": [0.3, 0.5, 0.7, 1.0, 1.4]},
    {"sector": "Financials",             "sector_kr": "금융", "eps_revision_pct_week": 1.1, "upgrade_ratio": 0.61, "momentum": "↑상승중", "sparkline": [0.4, 0.6, 0.7, 0.9, 1.1]},
    {"sector": "Energy",                 "sector_kr": "에너지", "eps_revision_pct_week": 0.7, "upgrade_ratio": 0.55, "momentum": "→횡보", "sparkline": [0.9, 0.6, 0.5, 0.7, 0.7]},
    {"sector": "Industrials",            "sector_kr": "산업재", "eps_revision_pct_week": 0.5, "upgrade_ratio": 0.53, "momentum": "→횡보", "sparkline": [0.3, 0.4, 0.5, 0.5, 0.5]},
    {"sector": "Health Care",            "sector_kr": "헬스케어", "eps_revision_pct_week": 0.3, "upgrade_ratio": 0.50, "momentum": "→횡보", "sparkline": [0.2, 0.3, 0.4, 0.3, 0.3]},
    {"sector": "Consumer Discretionary", "sector_kr": "경기소비재", "eps_revision_pct_week": 0.1, "upgrade_ratio": 0.48, "momentum": "↓하락중", "sparkline": [0.5, 0.4, 0.3, 0.2, 0.1]},
    {"sector": "Real Estate",            "sector_kr": "부동산", "eps_revision_pct_week": -0.2, "upgrade_ratio": 0.42, "momentum": "↓하락중", "sparkline": [0.1, 0.0, -0.1, -0.2, -0.2]},
    {"sector": "Materials",              "sector_kr": "소재", "eps_revision_pct_week": -0.4, "upgrade_ratio": 0.38, "momentum": "↓하락중", "sparkline": [0.0, -0.1, -0.2, -0.3, -0.4]},
    {"sector": "Consumer Staples",       "sector_kr": "필수소비재", "eps_revision_pct_week": -0.6, "upgrade_ratio": 0.35, "momentum": "↓하락중", "sparkline": [-0.1, -0.2, -0.3, -0.5, -0.6]},
    {"sector": "Utilities",              "sector_kr": "유틸리티", "eps_revision_pct_week": -0.9, "upgrade_ratio": 0.30, "momentum": "↓하락중", "sparkline": [-0.2, -0.4, -0.6, -0.8, -0.9]},
]

# ── M3 실적 개선 기업 ──────────────────────────────────────────────
M3_DATA = [
    {"rank": 1, "ticker": "NVDA", "name": "Nvidia", "sector": "IT", "market_cap_b": 2800, "revenue_growth_q": [42, 55, 68, 78], "op_margin_q": [22, 25, 28, 32], "eps_surprise_q": [8.2, 12.4], "key_driver": "AI 데이터센터 수요 급증, H100·B200 공급 확대 및 Blackwell 아키텍처 전환 가속", "next_q_consensus_eps": 0.89},
    {"rank": 2, "ticker": "META", "name": "Meta Platforms", "sector": "커뮤니케이션", "market_cap_b": 1450, "revenue_growth_q": [23, 27, 32, 41], "op_margin_q": [28, 31, 34, 38], "eps_surprise_q": [5.1, 8.7], "key_driver": "광고 AI 최적화로 광고단가 23% 상승, 릴스 DAU 10억 돌파", "next_q_consensus_eps": 5.24},
    {"rank": 3, "ticker": "AVGO", "name": "Broadcom", "sector": "IT", "market_cap_b": 890, "revenue_growth_q": [31, 38, 47, 58], "op_margin_q": [33, 35, 37, 40], "eps_surprise_q": [4.3, 6.8], "key_driver": "구글·애플 등 하이퍼스케일러 맞춤 AI칩(XPU) 수주 급증, VMware 통합 시너지", "next_q_consensus_eps": 1.48},
    {"rank": 4, "ticker": "ORCL", "name": "Oracle", "sector": "IT", "market_cap_b": 420, "revenue_growth_q": [18, 22, 26, 31], "op_margin_q": [30, 32, 34, 37], "eps_surprise_q": [3.1, 5.2], "key_driver": "OCI(오라클 클라우드) AI 인프라 계약 잔고 990억달러 돌파", "next_q_consensus_eps": 1.62},
    {"rank": 5, "ticker": "PLTR", "name": "Palantir", "sector": "IT", "market_cap_b": 180, "revenue_growth_q": [20, 25, 30, 39], "op_margin_q": [8, 12, 16, 21], "eps_surprise_q": [28.5, 41.2], "key_driver": "US 상업 부문 AI 플랫폼 수요 가속, AIP 계약 건수 분기 대비 2배 증가", "next_q_consensus_eps": 0.12},
    {"rank": 6, "ticker": "APP",  "name": "Applovin", "sector": "커뮤니케이션", "market_cap_b": 145, "revenue_growth_q": [28, 35, 44, 54], "op_margin_q": [18, 22, 28, 35], "eps_surprise_q": [18.3, 31.4], "key_driver": "AI 기반 모바일 광고 최적화 엔진 AXON 2.0 도입으로 ROAS 급상승", "next_q_consensus_eps": 1.38},
    {"rank": 7, "ticker": "ANET", "name": "Arista Networks", "sector": "IT", "market_cap_b": 135, "revenue_growth_q": [21, 26, 31, 37], "op_margin_q": [35, 36, 37, 39], "eps_surprise_q": [6.2, 9.1], "key_driver": "AI 데이터센터 네트워킹 수요 급증, 400G·800G 이더넷 스위치 점유율 확대", "next_q_consensus_eps": 2.18},
    {"rank": 8, "ticker": "PANW", "name": "Palo Alto Networks", "sector": "IT", "market_cap_b": 128, "revenue_growth_q": [19, 22, 25, 28], "op_margin_q": [15, 17, 19, 22], "eps_surprise_q": [4.1, 7.2], "key_driver": "플랫폼화 전략 성공, ARR 40억달러 돌파 및 차세대 보안 번들 채택 가속", "next_q_consensus_eps": 0.78},
    {"rank": 9, "ticker": "CRWD", "name": "CrowdStrike", "sector": "IT", "market_cap_b": 92, "revenue_growth_q": [33, 36, 39, 42], "op_margin_q": [14, 16, 19, 22], "eps_surprise_q": [5.8, 8.3], "key_driver": "Falcon 플랫폼 확장 지속, 모듈당 ARR 상승 및 NET NEW ARR 가이던스 상향", "next_q_consensus_eps": 0.93},
    {"rank": 10, "ticker": "AXON", "name": "Axon Enterprise", "sector": "산업재", "market_cap_b": 48, "revenue_growth_q": [24, 28, 33, 38], "op_margin_q": [10, 13, 16, 19], "eps_surprise_q": [12.4, 18.6], "key_driver": "AI 기반 경찰 보디캠·드론 플랫폼 수요 급증, Draft One AI 검사보고서 구독 확대", "next_q_consensus_eps": 1.14},
]

# ── M4 흑자전환 예상 기업 ──────────────────────────────────────────
M4_DATA = [
    # current_price·projected_pe 는 generate_invest.py 에서 yfinance 현재가로 갱신/계산.
    # consensus_eps 는 연환산. projected_pe = current_price / (consensus_eps × 4분기) 추정.
    {"rank": 1, "ticker": "RIVN", "name": "Rivian", "market_cap_b": 14, "turnaround_quarter": "2025Q3", "consensus_eps": 0.12, "analyst_count": 18, "current_price": 13.5, "projected_pe": 28.1, "catalyst": "생산 효율화로 단위당 손실 $2.1 → $0.3 개선, R2 플랫폼 출시 기대", "risk": "원자재 가격 재상승 시 전환 지연 가능", "recent_eps": [-1.08, -0.95]},
    {"rank": 2, "ticker": "SMCI", "name": "Super Micro", "market_cap_b": 28, "turnaround_quarter": "2025Q2", "consensus_eps": 0.48, "analyst_count": 12, "current_price": 48.0, "projected_pe": 25.0, "catalyst": "회계 감사 완료 후 나스닥 상장폐지 위기 해소, AI 서버 수주 재개", "risk": "감사 재지연 시 투자심리 급랭", "recent_eps": [-0.32, -0.14]},
    {"rank": 3, "ticker": "BIRD", "name": "Allbirds", "market_cap_b": 0.3, "turnaround_quarter": "2025Q4", "consensus_eps": 0.04, "analyst_count": 5, "current_price": 8.5, "projected_pe": 53.1, "catalyst": "SKU 축소·고마진 제품 집중으로 매출총이익률 8%p 개선", "risk": "소비 침체 지속 시 매출 회복 지연", "recent_eps": [-0.18, -0.11]},
    {"rank": 4, "ticker": "XPEV", "name": "XPeng", "market_cap_b": 12, "turnaround_quarter": "2025Q3", "consensus_eps": 0.08, "analyst_count": 14, "current_price": 12.8, "projected_pe": 40.0, "catalyst": "MONA M03 흥행으로 분기 인도량 3만대 돌파, 원가율 개선 지속", "risk": "중국 보조금 정책 변경 및 BYD 가격경쟁 심화", "recent_eps": [-0.41, -0.28]},
    {"rank": 5, "ticker": "LCID", "name": "Lucid Motors", "market_cap_b": 7, "turnaround_quarter": "2026Q1", "consensus_eps": 0.06, "analyst_count": 8, "current_price": 2.9, "projected_pe": 12.1, "catalyst": "사우디 아람코 투자유치 및 Gravity SUV 출시, 생산능력 2만대 확충", "risk": "자금소진 속도 빨라 추가 자본조달 필요", "recent_eps": [-0.29, -0.22]},
    {"rank": 6, "ticker": "JOBY", "name": "Joby Aviation", "market_cap_b": 6, "turnaround_quarter": "2026Q2", "consensus_eps": 0.09, "analyst_count": 7, "current_price": 6.2, "projected_pe": 17.2, "catalyst": "FAA 형식증명 승인 임박, UAE 에미레이트항공과 파일럿 서비스 계약 체결", "risk": "규제 승인 지연 시 상업화 일정 1년 이상 후퇴 가능", "recent_eps": [-0.14, -0.12]},
    {"rank": 7, "ticker": "IONQ", "name": "IonQ", "market_cap_b": 5, "turnaround_quarter": "2026Q1", "consensus_eps": 0.11, "analyst_count": 9, "current_price": 24.5, "projected_pe": 55.7, "catalyst": "양자컴퓨터 상업 계약 확대, 포르투갈 데이터센터 구축 완료", "risk": "양자우위 달성 시기 불확실, 경쟁사 IBM·Google 대비 상용화 격차", "recent_eps": [-0.18, -0.15]},
]

# ── M5 내부자 거래 ──────────────────────────────────────────────────
M5_DATA = {
    "period": "2025-05-05 ~ 2025-05-09",
    "buy": [
        {"ticker": "NVDA", "insider_name": "Jensen Huang", "title": "CEO", "transaction": "매수", "amount_usd": 8200000, "shares": 68000, "signal": "강한 매수 신호", "signal_type": "bullish"},
        {"ticker": "MSFT", "insider_name": "Satya Nadella", "title": "CEO", "transaction": "매수", "amount_usd": 3100000, "shares": 8200, "signal": "경영진 자신감 표출", "signal_type": "bullish"},
        {"ticker": "PLTR", "insider_name": "Alex Karp", "title": "CEO", "transaction": "매수", "amount_usd": 2400000, "shares": 92000, "signal": "내부자 2인 동시 매수 → 강한 신호", "signal_type": "strong_bullish"},
        {"ticker": "PLTR", "insider_name": "Peter Thiel", "title": "이사", "transaction": "매수", "amount_usd": 1800000, "shares": 69000, "signal": "내부자 2인 동시 매수 → 강한 신호", "signal_type": "strong_bullish"},
        {"ticker": "AXON", "insider_name": "Rick Smith", "title": "CEO", "transaction": "매수", "amount_usd": 1200000, "shares": 4100, "signal": "신고가 구간 임원 매수", "signal_type": "bullish"},
    ],
    "sell": [
        {"ticker": "META", "insider_name": "Mark Zuckerberg", "title": "CEO", "transaction": "매도", "amount_usd": 4500000, "shares_sold_pct": 0.8, "signal": "정기 매도 플랜(10b5-1), 경영 판단 아님", "signal_type": "neutral"},
        {"ticker": "AMZN", "insider_name": "Jeff Bezos", "title": "이사", "transaction": "매도", "amount_usd": 3200000, "shares_sold_pct": 0.3, "signal": "사전 설정 매도 플랜", "signal_type": "neutral"},
        {"ticker": "TSLA", "insider_name": "Elon Musk", "title": "CEO", "transaction": "매도", "amount_usd": 7800000, "shares_sold_pct": 1.2, "signal": "주의: 지분 10% 이상 매도 접근", "signal_type": "bearish"},
    ],
}

# ── M6 강세장 마감 신호 ──────────────────────────────────────────────
M6_DATA = {
    "semiconductor": [
        {"ticker": "NVDA", "eps_growth_q": [206, 265, 122, 78],  "trend": "둔화 초입"},
        {"ticker": "AMD",  "eps_growth_q": [48, 62, 71, 58],     "trend": "둔화 초입"},
        {"ticker": "AVGO", "eps_growth_q": [29, 38, 54, 61],     "trend": "지속 성장"},
        {"ticker": "ASML", "eps_growth_q": [41, 35, 28, 22],     "trend": "둔화 중"},
        {"ticker": "TSM",  "eps_growth_q": [33, 45, 54, 61],     "trend": "지속 성장"},
    ],
    "capex": [
        {"ticker": "META",  "capex_q_b": [8.5, 9.2, 10.8, 13.7], "yoy_growth_pct": 61, "guidance": "증가", "ai_ratio_pct": 72},
        {"ticker": "GOOGL", "capex_q_b": [12.0, 12.8, 13.1, 17.2],"yoy_growth_pct": 43, "guidance": "증가", "ai_ratio_pct": 68},
        {"ticker": "MSFT",  "capex_q_b": [14.1, 14.4, 14.9, 16.8],"yoy_growth_pct": 19, "guidance": "유지", "ai_ratio_pct": 65},
        {"ticker": "AMZN",  "capex_q_b": [22.0, 23.8, 25.1, 28.4],"yoy_growth_pct": 29, "guidance": "증가", "ai_ratio_pct": 58},
        {"ticker": "AAPL",  "capex_q_b": [2.8, 2.9, 3.0, 3.1],   "yoy_growth_pct": 11, "guidance": "유지", "ai_ratio_pct": 40},
    ],
    "overall": {
        "semiconductor_growth_trend": "둔화 초입",
        "capex_trend": "확대",
        "bull_market_signal": "주의",
        "summary": "NVDA·AMD EPS 성장률 고점 통과 조짐이나 절대 성장률은 양호. 빅테크 CapEx는 META·GOOGL 주도로 여전히 확대 중. 단기 조정 리스크 존재하나 사이클 전환 신호는 아직 미확인.",
    },
    # 미국 시총 상위 20 + 전세계 반도체 상위 10 (NVDA/AVGO 중복 제외) = 30종목
    # mock 값은 yfinance 가 실시간 값으로 덮어씀
    "peg_ratios": [
        {"ticker": "TSLA",      "name": "Tesla",                "peg": 4.2, "pe": 68.4, "growth_rate": 16.3},
        {"ticker": "NVDA",      "name": "Nvidia",               "peg": 3.8, "pe": 42.1, "growth_rate": 11.1},
        {"ticker": "COST",      "name": "Costco",               "peg": 3.5, "pe": 52.0, "growth_rate": 14.9},
        {"ticker": "AAPL",      "name": "Apple",                "peg": 2.9, "pe": 28.8, "growth_rate":  9.9},
        {"ticker": "HD",        "name": "Home Depot",           "peg": 2.7, "pe": 26.5, "growth_rate":  9.8},
        {"ticker": "MSFT",      "name": "Microsoft",            "peg": 2.6, "pe": 31.2, "growth_rate": 12.0},
        {"ticker": "V",         "name": "Visa",                 "peg": 2.4, "pe": 28.1, "growth_rate": 11.7},
        {"ticker": "MA",        "name": "Mastercard",           "peg": 2.3, "pe": 30.5, "growth_rate": 13.3},
        {"ticker": "AMD",       "name": "AMD",                  "peg": 2.2, "pe": 45.0, "growth_rate": 20.5},
        {"ticker": "WMT",       "name": "Walmart",              "peg": 2.1, "pe": 32.0, "growth_rate": 15.2},
        {"ticker": "NFLX",      "name": "Netflix",              "peg": 1.9, "pe": 38.5, "growth_rate": 20.3},
        {"ticker": "META",      "name": "Meta",                 "peg": 1.8, "pe": 23.4, "growth_rate": 13.0},
        {"ticker": "LLY",       "name": "Eli Lilly",            "peg": 1.8, "pe": 30.5, "growth_rate": 16.9},
        {"ticker": "AVGO",      "name": "Broadcom",             "peg": 1.5, "pe": 34.5, "growth_rate": 23.0},
        {"ticker": "ORCL",      "name": "Oracle",               "peg": 1.5, "pe": 25.1, "growth_rate": 16.7},
        {"ticker": "ARM",       "name": "ARM Holdings",         "peg": 1.4, "pe": 75.0, "growth_rate": 53.6},
        {"ticker": "AMZN",      "name": "Amazon",               "peg": 1.4, "pe": 36.8, "growth_rate": 26.3},
        {"ticker": "AMAT",      "name": "Applied Materials",    "peg": 1.3, "pe": 20.2, "growth_rate": 15.5},
        {"ticker": "QCOM",      "name": "Qualcomm",             "peg": 1.3, "pe": 17.5, "growth_rate": 13.5},
        {"ticker": "ASML",      "name": "ASML",                 "peg": 1.2, "pe": 35.0, "growth_rate": 29.2},
        {"ticker": "TSM",       "name": "TSMC",                 "peg": 1.2, "pe": 26.8, "growth_rate": 22.3},
        {"ticker": "TXN",       "name": "Texas Instruments",    "peg": 1.2, "pe": 31.0, "growth_rate": 25.8},
        {"ticker": "GOOGL",     "name": "Alphabet",             "peg": 1.1, "pe": 19.8, "growth_rate": 18.0},
        {"ticker": "BRK-B",     "name": "Berkshire",            "peg": 1.0, "pe": 22.5, "growth_rate": 22.5},
        {"ticker": "JPM",       "name": "JPMorgan",             "peg": 1.0, "pe": 13.0, "growth_rate": 13.0},
        {"ticker": "MU",        "name": "Micron",               "peg": 1.0, "pe": 15.0, "growth_rate": 15.0},
        {"ticker": "XOM",       "name": "ExxonMobil",           "peg": 0.9, "pe": 14.5, "growth_rate": 16.1},
        {"ticker": "JNJ",       "name": "Johnson & Johnson",    "peg": 0.9, "pe": 15.2, "growth_rate": 16.9},
        {"ticker": "005930.KS", "name": "삼성전자",              "peg": 0.8, "pe": 14.0, "growth_rate": 17.5},
        {"ticker": "000660.KS", "name": "SK하이닉스",            "peg": 0.6, "pe":  9.5, "growth_rate": 15.8},
    ],
}

# ── M7 미국 시총 상위 50종목 5지표 + 신호등 ────────────────────────
# yfinance 가 실시간 값으로 덮어씀. mock 시드는 fallback 용도.
def _sig_pe(pe):  return "green" if pe < 15 else "yellow" if pe <= 25 else "red"
def _sig_peg(g):  return "green" if g  < 1.0 else "yellow" if g  <= 1.5 else "red"
def _sig_gr(p):   return "green" if p  > 15  else "yellow" if p  >= 5   else "red"
def _sig_tr(a):   return {"↑":"green","→":"yellow","↓":"red"}.get(a, "yellow")

def _row(t, n, pe, peg, rev, eps, tr):
    return {
        "ticker": t, "name": n, "pe": pe, "peg": peg,
        "rev_growth": rev, "eps_growth": eps, "eps_trend": tr,
        "sig_pe": _sig_pe(pe), "sig_peg": _sig_peg(peg),
        "sig_rev": _sig_gr(rev), "sig_eps": _sig_gr(eps), "sig_trend": _sig_tr(tr),
    }

# ── M8 한국 시총 상위 50종목 5지표 + 신호등 ────────────────────────
# yfinance 가 실시간 값으로 덮어씀. 아래 mock 은 fallback 용.
M8_DATA = {
    "stocks": [
        _row("005930.KS", "삼성전자",         14.0, 0.8, 17.5, 35.7, "↑"),
        _row("000660.KS", "SK하이닉스",        9.5, 0.6, 15.8, 138.2, "↑"),
        _row("373220.KS", "LG에너지솔루션",   80.0, 3.5, -8.0, -5.0, "↓"),
        _row("207940.KS", "삼성바이오로직스", 60.0, 2.8, 22.0, 25.0, "↑"),
        _row("005380.KS", "현대차",            5.5, 0.6,  8.0, 12.0, "→"),
        _row("000270.KS", "기아",              4.5, 0.5,  9.0, 14.0, "→"),
        _row("005490.KS", "POSCO홀딩스",      14.0, 2.0, -3.0, -10.0, "↓"),
        _row("035420.KS", "NAVER",            22.0, 1.4, 10.0, 14.0, "↑"),
        _row("005935.KS", "삼성전자우",       12.5, 0.7, 17.5, 35.0, "↑"),
        _row("105560.KS", "KB금융",            6.0, 0.9,  7.0,  8.0, "→"),
        _row("035720.KS", "카카오",           32.0, 2.2,  4.0,  6.0, "→"),
        _row("068270.KS", "셀트리온",         35.0, 1.5, 18.0, 25.0, "↑"),
        _row("028260.KS", "삼성물산",         16.0, 1.5,  6.0,  9.0, "→"),
        _row("055550.KS", "신한지주",          5.5, 0.8,  6.0,  9.0, "→"),
        _row("012330.KS", "현대모비스",        7.0, 1.0,  5.0,  8.0, "→"),
        _row("138040.KS", "메리츠금융지주",    5.0, 0.5, 10.0, 13.0, "↑"),
        _row("086790.KS", "하나금융지주",      4.8, 0.7,  6.0,  8.0, "→"),
        _row("006400.KS", "삼성SDI",          30.0, 2.5, -2.0, -8.0, "↓"),
        _row("051910.KS", "LG화학",           18.0, 1.8,  3.0,  6.0, "→"),
        _row("015760.KS", "한국전력",         10.0, 1.0,  2.0,  4.0, "→"),
        _row("011200.KS", "HMM",               4.0, 0.4, 30.0, 45.0, "↑"),
        _row("032830.KS", "삼성생명",          9.0, 1.1,  4.0,  6.0, "→"),
        _row("003670.KS", "포스코퓨처엠",     45.0, 3.0, -5.0, -10.0, "↓"),
        _row("009150.KS", "삼성전기",         18.0, 1.4,  9.0, 14.0, "↑"),
        _row("010130.KS", "고려아연",         16.0, 1.6, 10.0, 12.0, "→"),
        _row("034730.KS", "SK",               10.0, 1.0,  5.0,  7.0, "→"),
        _row("010950.KS", "S-Oil",             8.0, 0.8,  3.0,  5.0, "→"),
        _row("011170.KS", "롯데케미칼",       40.0, 2.5, -10.0, -15.0, "↓"),
        _row("251270.KS", "넷마블",           28.0, 2.0,  6.0,  9.0, "→"),
        _row("036570.KS", "엔씨소프트",       22.0, 1.8,  2.0,  4.0, "→"),
        _row("017670.KS", "SK텔레콤",         10.0, 1.5,  2.0,  4.0, "→"),
        _row("030200.KS", "KT",                8.0, 1.4,  2.0,  3.5, "→"),
        _row("018260.KS", "삼성에스디에스",   18.0, 1.5,  5.0,  8.0, "→"),
        _row("003550.KS", "LG",                7.0, 0.9,  4.0,  6.0, "→"),
        _row("000810.KS", "삼성화재",          8.0, 0.9,  5.0,  7.0, "→"),
        _row("024110.KS", "기업은행",          5.0, 0.8,  5.0,  7.0, "→"),
        _row("033780.KS", "KT&G",             10.0, 1.6,  3.0,  5.0, "→"),
        _row("066570.KS", "LG전자",            8.0, 0.8,  6.0,  9.0, "→"),
        _row("047810.KS", "한국항공우주",     22.0, 1.5, 12.0, 18.0, "↑"),
        _row("003490.KS", "대한항공",          7.0, 0.9,  4.0,  7.0, "→"),
        _row("009830.KS", "한화솔루션",       16.0, 2.0,  3.0,  5.0, "→"),
        _row("042660.KS", "한화오션",         30.0, 1.5, 18.0, 28.0, "↑"),
        _row("010140.KS", "삼성중공업",       20.0, 1.4, 16.0, 24.0, "↑"),
        _row("064350.KS", "현대로템",         20.0, 1.3, 15.0, 22.0, "↑"),
        _row("326030.KS", "SK바이오팜",       40.0, 2.0, 12.0, 18.0, "↑"),
        _row("247540.KQ", "에코프로비엠",     60.0, 4.0, -12.0, -20.0, "↓"),
        _row("086520.KQ", "에코프로",         50.0, 3.5, -10.0, -18.0, "↓"),
        _row("196170.KQ", "알테오젠",         80.0, 2.5, 35.0, 50.0, "↑"),
        _row("097950.KS", "CJ제일제당",       11.0, 1.2,  4.0,  6.0, "→"),
        _row("034220.KS", "LG디스플레이",     15.0, 1.0, 10.0, 15.0, "→"),
    ],
}

M7_DATA = {
    "stocks": [
        _row("AAPL",  "Apple",              28.8, 2.9,  9.9, 12.0, "↑"),
        _row("MSFT",  "Microsoft",          31.2, 2.6, 12.0, 15.1, "↑"),
        _row("NVDA",  "Nvidia",             42.1, 3.8, 78.0, 95.0, "↑"),
        _row("GOOGL", "Alphabet",           19.8, 1.1, 18.0, 22.0, "↑"),
        _row("AMZN",  "Amazon",             36.8, 1.4, 11.0, 26.3, "↑"),
        _row("META",  "Meta",               23.4, 1.8, 13.0, 18.0, "↑"),
        _row("TSLA",  "Tesla",              68.4, 4.2, 16.3,  8.0, "→"),
        _row("BRK-B", "Berkshire",          22.5, 1.0,  9.0, 11.0, "→"),
        _row("AVGO",  "Broadcom",           34.5, 1.5, 23.0, 28.0, "↑"),
        _row("WMT",   "Walmart",            32.0, 2.1, 15.2,  8.0, "→"),
        _row("JPM",   "JPMorgan",           13.0, 1.0, 10.0, 13.0, "↑"),
        _row("ORCL",  "Oracle",             25.1, 1.5, 16.7, 14.0, "↑"),
        _row("LLY",   "Eli Lilly",          30.5, 1.8, 35.0, 40.0, "↑"),
        _row("V",     "Visa",               28.1, 2.4, 11.7, 13.0, "↑"),
        _row("MA",    "Mastercard",         30.5, 2.3, 13.3, 14.0, "↑"),
        _row("NFLX",  "Netflix",            38.5, 1.9, 20.3, 25.0, "↑"),
        _row("XOM",   "ExxonMobil",         14.5, 0.9,  8.0, 16.1, "→"),
        _row("COST",  "Costco",             52.0, 3.5,  7.0, 14.9, "→"),
        _row("JNJ",   "Johnson & Johnson",  15.2, 0.9,  6.0, 16.9, "→"),
        _row("HD",    "Home Depot",         26.5, 2.7,  9.8,  4.0, "→"),
        _row("PG",    "P&G",                25.0, 3.0,  3.5,  7.0, "→"),
        _row("BAC",   "Bank of America",    12.0, 1.1,  8.0, 10.0, "→"),
        _row("ABBV",  "AbbVie",             18.0, 2.0,  4.0,  6.0, "→"),
        _row("KO",    "Coca-Cola",          24.0, 3.4,  3.0,  5.0, "→"),
        _row("CVX",   "Chevron",            13.5, 1.0,  7.0, 14.0, "→"),
        _row("CRM",   "Salesforce",         42.0, 2.4, 11.0, 18.0, "↑"),
        _row("AMD",   "AMD",                45.0, 2.2, 20.5, 25.0, "↑"),
        _row("MRK",   "Merck",              16.0, 1.4,  7.0,  9.0, "→"),
        _row("TMO",   "Thermo Fisher",      28.0, 2.5,  3.5,  6.0, "→"),
        _row("PEP",   "PepsiCo",            22.5, 3.0,  4.5,  7.0, "→"),
        _row("ACN",   "Accenture",          27.0, 2.6,  5.0,  9.0, "→"),
        _row("ADBE",  "Adobe",              32.0, 1.8, 11.0, 16.0, "↑"),
        _row("LIN",   "Linde",              30.0, 3.5,  5.0,  9.0, "→"),
        _row("MCD",   "McDonald's",         24.0, 3.0,  4.0,  7.0, "→"),
        _row("CSCO",  "Cisco",              18.0, 2.0,  6.0,  8.0, "→"),
        _row("ABT",   "Abbott",             24.5, 2.7,  5.5,  8.0, "→"),
        _row("IBM",   "IBM",                21.0, 2.2,  4.0,  6.0, "→"),
        _row("GE",    "GE Aerospace",       35.0, 2.5, 11.0, 18.0, "↑"),
        _row("NOW",   "ServiceNow",         60.0, 2.6, 22.0, 28.0, "↑"),
        _row("AXP",   "American Express",   19.0, 1.6, 10.0, 14.0, "↑"),
        _row("PM",    "Philip Morris",      20.0, 2.3,  6.0,  9.0, "→"),
        _row("DIS",   "Disney",             21.0, 1.4,  5.0, 12.0, "↑"),
        _row("INTU",  "Intuit",             54.0, 3.0, 13.0, 18.0, "↑"),
        _row("T",     "AT&T",               12.0, 2.7,  1.5,  6.0, "→"),
        _row("MS",    "Morgan Stanley",     14.0, 1.0,  9.0, 12.0, "↑"),
        _row("ISRG",  "Intuitive Surgical", 65.0, 3.4, 18.0, 24.0, "↑"),
        _row("CAT",   "Caterpillar",        16.0, 1.7,  4.0,  9.0, "→"),
        _row("GS",    "Goldman Sachs",      14.0, 1.2,  8.0, 14.0, "↑"),
        _row("VZ",    "Verizon",            10.0, 2.8,  1.0,  3.0, "→"),
        _row("RTX",   "RTX",                18.0, 1.9,  6.0,  8.0, "→"),
    ],
}

# ── 종합 판단 Summary ──────────────────────────────────────────────
SUMMARY_DATA = {
    "date": TODAY,
    "stance": "선별적 매수",
    "stance_level": 2,  # 1=공격적매수 2=선별적매수 3=중립 4=방어적
    "top_sectors": [
        {"rank": 1, "name": "IT·기술", "reason": "EPS 상향 1.8%, AI 인프라 수요 지속"},
        {"rank": 2, "name": "커뮤니케이션", "reason": "광고 수익성 개선, 메타·알파벳 실적 서프라이즈"},
        {"rank": 3, "name": "금융", "reason": "금리 고점 인식으로 NIM 안정, 신용손실 예상 하회"},
    ],
    "screened_stocks": [
        {"ticker": "NVDA", "reason": "M3 1위 + M1 대가 다수 보유 + M5 CEO 매수"},
        {"ticker": "PLTR", "reason": "M3 5위(실적가속) + M5 임원 2인 동시 매수"},
        {"ticker": "AXON", "reason": "M3 10위 + M5 CEO 매수 + M1 드러켄밀러 편입"},
        {"ticker": "AVGO", "reason": "M3 3위 + M6 반도체 성장 지속 + 대가 보유"},
        {"ticker": "APP",  "reason": "M3 6위(EPS 가속) + M1 드러켄밀러 신규편입"},
    ],
    "weekly_message": {
        "market_env": "AI 인프라 투자 사이클 중반부, 반도체 성장 둔화 초입 진입",
        "key_change": "NVDA CEO 젠슨황 820만달러 자사주 매수 — 실적 자신감 시그널",
        "next_event": "5/13 CPI 발표, 5/14 NVDA·CSCO 실적 발표",
    },
    "kakao_brief": f"""📊 [{TODAY}] 투자 브리핑

🎯 스탠스: 선별적 매수

📈 주목 섹터: IT·기술 / 커뮤니케이션 / 금융

✅ 이번 주 픽
· NVDA — CEO 820만달러 자사주 매수 + AI 수요 가속
· PLTR — 임원 2인 동시 매수 + AIP 계약 2배 성장
· AXON — 보디캠·드론 AI 플랫폼 수요 급증

⚠️ 주의 신호
· 반도체 EPS 성장률 YoY 둔화 초입 (NVDA·AMD)
· TSLA CEO 대규모 매도 지속 (경계)

📌 다음 주 이벤트
· 5/13 CPI 발표 / 5/14 NVDA 실적""",
}

# ── 투자 뉴스 ────────────────────────────────────────────────────
NEWS_DATA = [
    {
        "title": "젠슨 황 CEO, NVDA 주식 820만 달러 자사주 매수 — 실적 자신감 최고조",
        "source": "Bloomberg",
        "url": "https://www.bloomberg.com",
        "summary": "엔비디아 CEO 젠슨 황이 개인 자격으로 자사 주식 약 6.8만 주(820만 달러)를 장내 매수했다. 이는 블랙웰 아키텍처 수요가 공급을 초과하는 상황에서 경영진의 자신감을 보여주는 강력한 시그널이다.",
        "insight": "내부자 매수 + AI 수요 가속화의 이중 강세 신호. NVDA 비중 확대 근거로 활용 가능.",
        "stars": 5
    },
    {
        "title": "OpenAI, 기업용 API 가격 40% 인하 — AI 인프라 수요 폭발 예고",
        "source": "The Information",
        "url": "https://www.theinformation.com",
        "summary": "OpenAI가 GPT-4o API 가격을 40% 대폭 인하하며 기업 고객 확장에 나섰다. AI 서비스 대중화로 데이터센터 트래픽이 급증할 전망이며 NVDA, AVGO, ANET 등 인프라 수혜가 예상된다.",
        "insight": "AI 소프트웨어 경쟁 심화 → 클라우드 인프라 수요 가속. NVDA·AVGO·ANET 간접 수혜.",
        "stars": 5
    },
    {
        "title": "Meta, 2026년 AI 인프라 CapEx 650억 달러로 상향 — 광고 AI 수익성 급등",
        "source": "Wall Street Journal",
        "url": "https://www.wsj.com",
        "summary": "메타가 2026년 설비투자 가이던스를 기존 600억 달러에서 650억 달러로 상향 조정했다. Llama AI 광고 최적화 엔진이 클릭율을 32% 끌어올리며 광고 단가 상승이 이어지고 있다.",
        "insight": "META 광고 AI ROI 입증. 실적 가이던스 상향 가능성 높아 비중 유지 또는 확대 검토.",
        "stars": 5
    },
    {
        "title": "Palantir, 미 국방부 AIP 계약 15억 달러 추가 수주 — 정부 AI 플랫폼 독점화",
        "source": "Reuters",
        "url": "https://www.reuters.com",
        "summary": "팔란티어가 미 국방부와 AIP(AI 플랫폼) 계약 15억 달러를 추가 체결했다. 미 정부의 AI 예산 확대 기조 속에 팔란티어의 정부 부문 매출이 YoY 45% 성장 전망이다.",
        "insight": "PLTR 정부 수주 모멘텀 지속. 밸류에이션 부담(PEG 5.1)에도 성장 가속 구간으로 단기 강세 유효.",
        "stars": 4
    },
    {
        "title": "Microsoft, Copilot 기업 구독자 50만 명 돌파 — AI 수익화 본격화",
        "source": "CNBC",
        "url": "https://www.cnbc.com",
        "summary": "마이크로소프트의 AI 코파일럿 기업 구독자가 50만 명을 넘어섰다. 월 30달러 구독료 기준 연간 ARR 18억 달러 규모로, Azure AI 사업과의 시너지로 클라우드 매출 성장률 재가속이 기대된다.",
        "insight": "MSFT AI 수익화 궤도 진입 확인. PEG 2.6으로 빅테크 중 밸류에이션 매력도 상위권.",
        "stars": 4
    },
    {
        "title": "TSMC, 2나노 수율 80% 달성 — 애플·엔비디아 2026 물량 확보 경쟁",
        "source": "Nikkei Asia",
        "url": "https://asia.nikkei.com",
        "summary": "TSMC의 2nm 공정 수율이 80%를 돌파하며 양산 체제에 진입했다. 애플 A20, 엔비디아 Rubin GPU 등 주요 고객사들이 이미 2026년 생산 물량의 70%를 사전 예약한 것으로 알려졌다.",
        "insight": "TSMC 기술 우위 재확인. NVDA 차세대 칩 공급 안정성 확보 → 중장기 성장 가시성 제고.",
        "stars": 4
    },
    {
        "title": "Amazon AWS, AI 특화 리전 3개 추가 신설 — CapEx 280억 달러 집행 예고",
        "source": "TechCrunch",
        "url": "https://techcrunch.com",
        "summary": "아마존이 AI 워크로드 전용 AWS 리전 3개를 신규 건설한다고 발표했다. 2025년 CapEx 280억 달러 중 60% 이상이 AI 인프라에 집중될 예정으로, AI 수요 강세를 반영한 공격적 투자다.",
        "insight": "AMZN AWS AI 인프라 투자 확대 → NVDA 칩 수요 직접 연결. AMZN 클라우드 매출 재가속 기대.",
        "stars": 3
    },
    {
        "title": "Broadcom XPU 수주 잔고 200억 달러 — 구글·애플 맞춤형 AI칩 급성장",
        "source": "Barron's",
        "url": "https://www.barrons.com",
        "summary": "브로드컴의 맞춤형 AI 가속기(XPU) 수주 잔고가 200억 달러를 넘어섰다. 구글 TPU v5, 애플 Neural Engine 등 하이퍼스케일러 전용 칩 설계로 NVDA와 차별화된 수익 구조를 구축하고 있다.",
        "insight": "AVGO XPU 비즈니스 성장 가속 확인. PEG 1.5로 반도체 중 상대적 밸류에이션 매력 보유.",
        "stars": 3
    },
    {
        "title": "연준 FOMC 의사록 공개 — '금리 인하 서두르지 않겠다' 매파 기조 유지",
        "source": "Federal Reserve",
        "url": "https://www.federalreserve.gov",
        "summary": "5월 FOMC 의사록에서 연준 위원 대다수가 인플레이션 목표 달성까지 금리 인하를 자제해야 한다는 입장을 재확인했다. 시장은 9월 첫 인하 가능성을 55%로 소폭 낮춰 잡았다.",
        "insight": "고금리 지속 → 성장주 밸류에이션 압박 요인. 단기 변동성 확대 가능. 실적 우량주 중심 선별 투자 유효.",
        "stars": 3
    },
    {
        "title": "Applovin AXON 2.0, 광고 ROAS 업계 평균 3배 — 모바일 광고 시장 판도 변화",
        "source": "Business Insider",
        "url": "https://www.businessinsider.com",
        "summary": "앱러빈의 AI 광고 엔진 AXON 2.0이 광고주 ROAS(광고비 대비 수익)에서 업계 평균의 3배를 기록하며 구글·메타 광고 예산을 흡수하고 있다. Q2 매출 성장률이 55%를 상회할 것으로 전망된다.",
        "insight": "APP 모바일 광고 AI 경쟁력 압도적. 고PEG(2.2) 부담에도 EPS 가속 구간으로 단기 모멘텀 강세.",
        "stars": 2
    },
]
