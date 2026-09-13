"""
Claude(Opus 5 + 웹검색) 기반 분석 (주간 실행).
- analyze_stock : 종목 심층분석 (기업의 질 / 재무 건전성 / 가격 매력 / 촉매 / 반대 근거)
- analyze_stock_with_stats : 모델 지정 + 호출별 사용량·추정비용 반환 (모델 비교용)
- market_brief  : 주간 시장 스탠스 + 핵심 뉴스 10선 (실제 기사 URL)

결과는 strict 스키마의 submit 도구로 받는다. ANTHROPIC_API_KEY 미설정 시 호출하지 않음.
"""
import json
import os
import threading
import time

import anthropic

MODEL = "claude-opus-5"
# $ / 1M tokens (입력, 출력)
PRICES = {"claude-opus-5": (5.0, 25.0), "claude-sonnet-5": (2.0, 10.0)}
WEB_SEARCH_PRICE = 0.01  # $10 / 1,000회

_usage_lock = threading.Lock()
USAGE = {}  # model → 누적 사용량


def available():
    return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


def _cost(model, input_tokens, output_tokens, web_searches):
    p_in, p_out = PRICES[model]
    return (input_tokens * p_in + output_tokens * p_out) / 1e6 + web_searches * WEB_SEARCH_PRICE


def usage_summary():
    with _usage_lock:
        return {m: {**u, "est_cost_usd": round(_cost(m, u["input_tokens"], u["output_tokens"], u["web_searches"]), 2)}
                for m, u in USAGE.items()}


def _add_usage(stats, model, u):
    stu = getattr(u, "server_tool_use", None)
    delta = {
        "calls": 1,
        "input_tokens": (u.input_tokens or 0) + (u.cache_read_input_tokens or 0) + (u.cache_creation_input_tokens or 0),
        "output_tokens": u.output_tokens or 0,
        "web_searches": (getattr(stu, "web_search_requests", 0) or 0) if stu else 0,
    }
    for k, v in delta.items():
        stats[k] = stats.get(k, 0) + v
    with _usage_lock:
        total = USAGE.setdefault(model, {"calls": 0, "input_tokens": 0, "output_tokens": 0, "web_searches": 0})
        for k, v in delta.items():
            total[k] += v


def _run(system, user_text, submit_tool, max_searches, model=MODEL):
    """웹검색 + submit 도구 루프. (제출된 dict 또는 None, 이번 작업의 사용량·추정비용)"""
    client = anthropic.Anthropic(max_retries=4)
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": max_searches}, submit_tool]
    messages = [{"role": "user", "content": user_text}]
    # 거절 시 서버측 대체 모델 재시도는 Opus 5 에서만 사용
    extra = {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"} if model == "claude-opus-5" else {}
    stats, started, result = {"model": model}, time.time(), None
    for _ in range(6):
        with client.beta.messages.stream(
            model=model, max_tokens=32000, system=system, messages=messages, tools=tools,
            thinking={"type": "adaptive"}, **extra,
        ) as stream:
            resp = stream.get_final_message()
        _add_usage(stats, model, resp.usage)
        if resp.stop_reason == "refusal":
            print(f"  거절됨: {getattr(resp.stop_details, 'category', None)}")
            break
        result = next((b.input for b in resp.content if b.type == "tool_use" and b.name == submit_tool["name"]), None)
        if result is not None:
            break
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "pause_turn":
            messages.append({"role": "user", "content": f"조사를 마쳤다면 {submit_tool['name']} 도구로 결과를 제출하세요."})
    stats["seconds"] = round(time.time() - started)
    stats["est_cost_usd"] = round(_cost(model, stats.get("input_tokens", 0), stats.get("output_tokens", 0),
                                        stats.get("web_searches", 0)), 3)
    return result, stats


# ── 종목 심층분석 ────────────────────────────────────────────────
_SCORE = {"type": "integer", "enum": [1, 2, 3, 4, 5]}
_STR = {"type": "string"}


def _obj(props):
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


ANALYSIS_TOOL = {
    "name": "submit_analysis",
    "description": "종목 심층분석 결과를 제출한다. 조사를 마친 뒤 정확히 한 번 호출한다. 모든 서술은 한국어.",
    "strict": True,
    "input_schema": _obj({
        "one_line_thesis": _STR,
        "quality": _obj({"score": _SCORE, "moat": _STR, "growth_durability": _STR, "summary": _STR}),
        "financial_health": _obj({"score": _SCORE, "cash_flow": _STR, "debt": _STR, "dilution": _STR, "summary": _STR}),
        "valuation": _obj({"score": _SCORE, "current_view": _STR, "upside_scenario": _STR, "summary": _STR}),
        "catalysts": {"type": "array", "items": _obj({
            "event": _STR, "timing": _STR, "impact": {"type": "string", "enum": ["긍정", "부정", "불확실"]}, "detail": _STR})},
        "bear_case": _obj({"summary": _STR, "key_risks": {"type": "array", "items": _STR},
                           "thesis_breakers": {"type": "array", "items": _STR}}),
        "thesis_status": {"type": "string", "enum": ["유효", "약화", "붕괴", "해당없음"]},
        "thesis_status_reason": _STR,
        "verdict": {"type": "string", "enum": ["편입 적합", "관찰", "부적합"]},
        "verdict_reason": _STR,
        "conviction": _SCORE,
        "sources": {"type": "array", "items": _obj({"title": _STR, "url": _STR})},
    }),
}

ANALYSIS_SYSTEM = """당신은 미국 주식에 장기 투자하는 한국인 개인투자자를 돕는 주식 애널리스트입니다.
목표는 6개월 이상(가능하면 수년) 보유할 만한 기업인지 판단하는 것입니다. 단기 주가 흐름이 아니라 기업가치의 변화에 집중하세요.

제공되는 데이터 요약(Yahoo Finance 기준)을 출발점으로 삼되, 웹 검색으로 최근 실적 발표·가이던스·주요 뉴스(최근 3~6개월)를 직접 확인하세요. 데이터 요약과 최신 정보가 충돌하면 최신 정보를 따르고 그 사실을 서술에 밝히세요.

다섯 가지 관점으로 분석합니다.
1. 기업의 질: 경쟁우위(해자)의 실체와 지속성, 매출·이익 성장이 일회성인지 구조적인지.
2. 재무 건전성: 잉여현금흐름의 질(주식보상비용 반영), 부채 부담, 주식 희석 또는 자사주 매입.
3. 가격 매력: 성장 전망 대비 현재 밸류에이션. 동종업계·과거 대비 비싼지, 무엇이 맞아야 정당화되는지.
4. 향후 촉매: 6~12개월 안에 기업가치를 바꿀 구체적 사건과 예상 시점.
5. 반대 근거: 가장 강한 약세 논리, 그리고 투자 논리가 무너졌다고 판단할 관찰 가능한 조건(thesis_breakers).

판정 기준:
- '편입 적합'은 다섯 관점이 전반적으로 우호적이고, 반대 근거를 감안해도 6개월+ 보유의 기대값이 뚜렷할 때만 줍니다. 좋은 회사라도 가격이 이미 낙관을 반영했으면 '관찰'입니다.
- conviction(1~5)은 판정에 대한 확신도입니다. 5는 드물게 사용하세요.
- 억지로 긍정적인 결론을 만들지 마세요. '관찰'이나 '부적합'도 충분히 가치 있는 결론입니다.
- 이미 보유 중인 종목이면 기존 투자 논리와 논리 붕괴 조건을 최신 정보와 대조해 thesis_status(유효/약화/붕괴)를 판정하고 근거를 thesis_status_reason에 적습니다. 주가 하락 자체는 붕괴 사유가 아닙니다. 신규 후보는 thesis_status를 '해당없음'으로 둡니다.
- 각 서술은 구체적인 숫자와 사실을 담아 2~4문장으로 씁니다. sources에는 실제로 참고한 기사·공시의 제목과 URL을 넣습니다."""


def analyze_stock_with_stats(dossier, model=MODEL):
    held = dossier.get("holding")
    intro = (f"보유 중인 종목 {dossier['ticker']}의 투자 논리를 재점검하세요." if held
             else f"신규 편입 후보 {dossier['ticker']}를 분석하세요.")
    text = f"{intro}\n기준일: {dossier['as_of']}\n\n<data>\n{json.dumps(dossier, ensure_ascii=False, indent=1)}\n</data>"
    try:
        return _run(ANALYSIS_SYSTEM, text, ANALYSIS_TOOL, max_searches=5, model=model)
    except anthropic.APIError as e:
        print(f"  분석 실패 {dossier['ticker']} ({model}): {e}")
        return None, {"model": model, "error": str(e)}


def analyze_stock(dossier):
    return analyze_stock_with_stats(dossier)[0]


# ── 주간 시장 브리핑 ─────────────────────────────────────────────
MARKET_TOOL = {
    "name": "submit_market_brief",
    "description": "주간 시장 브리핑을 제출한다. 조사를 마친 뒤 정확히 한 번 호출한다. 모든 서술은 한국어.",
    "strict": True,
    "input_schema": _obj({
        "stance": {"type": "string", "enum": ["공격적 매수", "선별적 매수", "중립", "방어적"]},
        "stance_reason": _STR,
        "market_env": _STR,
        "key_change": _STR,
        "next_events": {"type": "array", "items": _obj({"date": _STR, "event": _STR})},
        "news": {"type": "array", "items": _obj({
            "title": _STR, "source": _STR, "url": _STR, "published": _STR, "summary": _STR, "insight": _STR,
            "stars": _SCORE, "tickers": {"type": "array", "items": _STR}})},
    }),
}

MARKET_SYSTEM = """당신은 미국 주식에 장기 투자하는 한국인 개인투자자를 위한 주간 시장 브리핑 담당자입니다.
웹 검색으로 지난 7일간 실제로 보도된 미국 증시·AI 산업·거시경제 뉴스를 확인하고, 장기 투자 판단에 의미 있는 기사 10건을 고르세요.
- 모든 기사는 검색 결과로 확인한 실제 기사여야 하며 url은 해당 기사 페이지 주소입니다. 확인하지 못한 기사는 넣지 마세요.
- stars(1~5)는 장기 투자자에게의 중요도, insight는 어떤 종목·섹터에 어떤 의미인지 1~2문장.
- stance는 제공된 섹터 추정치 흐름·사이클 지표와 뉴스를 종합해 정하고, stance_reason에 근거를 적습니다.
- next_events는 다음 7~10일 내 예정된 주요 일정(실적 발표, 경제지표, 연준 등)입니다."""


def market_brief(context):
    text = f"기준일: {context['as_of']}\n\n<data>\n{json.dumps(context, ensure_ascii=False, indent=1)}\n</data>"
    try:
        return _run(MARKET_SYSTEM, text, MARKET_TOOL, max_searches=10)[0]
    except anthropic.APIError as e:
        print(f"  시장 브리핑 실패: {e}")
        return None
