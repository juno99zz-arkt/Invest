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
    {"rank": 1, "ticker": "RIVN", "name": "Rivian", "market_cap_b": 14, "turnaround_quarter": "2025Q3", "consensus_eps": 0.12, "analyst_count": 18, "catalyst": "생산 효율화로 단위당 손실 $2.1 → $0.3 개선, R2 플랫폼 출시 기대", "risk": "원자재 가격 재상승 시 전환 지연 가능", "recent_eps": [-1.08, -0.95]},
    {"rank": 2, "ticker": "SMCI", "name": "Super Micro", "market_cap_b": 28, "turnaround_quarter": "2025Q2", "consensus_eps": 0.48, "analyst_count": 12, "catalyst": "회계 감사 완료 후 나스닥 상장폐지 위기 해소, AI 서버 수주 재개", "risk": "감사 재지연 시 투자심리 급랭", "recent_eps": [-0.32, -0.14]},
    {"rank": 3, "ticker": "BIRD", "name": "Allbirds", "market_cap_b": 0.3, "turnaround_quarter": "2025Q4", "consensus_eps": 0.04, "analyst_count": 5, "catalyst": "SKU 축소·고마진 제품 집중으로 매출총이익률 8%p 개선", "risk": "소비 침체 지속 시 매출 회복 지연", "recent_eps": [-0.18, -0.11]},
    {"rank": 4, "ticker": "XPEV", "name": "XPeng", "market_cap_b": 12, "turnaround_quarter": "2025Q3", "consensus_eps": 0.08, "analyst_count": 14, "catalyst": "MONA M03 흥행으로 분기 인도량 3만대 돌파, 원가율 개선 지속", "risk": "중국 보조금 정책 변경 및 BYD 가격경쟁 심화", "recent_eps": [-0.41, -0.28]},
    {"rank": 5, "ticker": "LCID", "name": "Lucid Motors", "market_cap_b": 7, "turnaround_quarter": "2026Q1", "consensus_eps": 0.06, "analyst_count": 8, "catalyst": "사우디 아람코 투자유치 및 Gravity SUV 출시, 생산능력 2만대 확충", "risk": "자금소진 속도 빨라 추가 자본조달 필요", "recent_eps": [-0.29, -0.22]},
    {"rank": 6, "ticker": "JOBY", "name": "Joby Aviation", "market_cap_b": 6, "turnaround_quarter": "2026Q2", "consensus_eps": 0.09, "analyst_count": 7, "catalyst": "FAA 형식증명 승인 임박, UAE 에미레이트항공과 파일럿 서비스 계약 체결", "risk": "규제 승인 지연 시 상업화 일정 1년 이상 후퇴 가능", "recent_eps": [-0.14, -0.12]},
    {"rank": 7, "ticker": "IONQ", "name": "IonQ", "market_cap_b": 5, "turnaround_quarter": "2026Q1", "consensus_eps": 0.11, "analyst_count": 9, "catalyst": "양자컴퓨터 상업 계약 확대, 포르투갈 데이터센터 구축 완료", "risk": "양자우위 달성 시기 불확실, 경쟁사 IBM·Google 대비 상용화 격차", "recent_eps": [-0.18, -0.15]},
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
    "peg_ratios": [
        {"ticker": "PLTR", "name": "Palantir",   "peg": 5.1,  "pe": 98.2,  "growth_rate": 19.3},
        {"ticker": "TSLA", "name": "Tesla",       "peg": 4.2,  "pe": 68.4,  "growth_rate": 16.3},
        {"ticker": "NVDA", "name": "Nvidia",      "peg": 3.8,  "pe": 42.1,  "growth_rate": 11.1},
        {"ticker": "APP",  "name": "Applovin",    "peg": 2.2,  "pe": 52.8,  "growth_rate": 24.0},
        {"ticker": "AAPL", "name": "Apple",       "peg": 2.9,  "pe": 28.8,  "growth_rate":  9.9},
        {"ticker": "MSFT", "name": "Microsoft",   "peg": 2.6,  "pe": 31.2,  "growth_rate": 12.0},
        {"ticker": "META", "name": "Meta",        "peg": 1.8,  "pe": 23.4,  "growth_rate": 13.0},
        {"ticker": "AVGO", "name": "Broadcom",    "peg": 1.5,  "pe": 34.5,  "growth_rate": 23.0},
        {"ticker": "AMZN", "name": "Amazon",      "peg": 1.4,  "pe": 36.8,  "growth_rate": 26.3},
        {"ticker": "GOOGL","name": "Alphabet",    "peg": 1.1,  "pe": 19.8,  "growth_rate": 18.0},
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
