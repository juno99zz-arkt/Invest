"""Auditable long-horizon screening. No mock fallback or invented research."""
import math
from datetime import datetime, timezone
from statistics import median

MODEL = "us-long-term-v1"


def number(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def age_days(value, now):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (now - dt).total_seconds() / 86400
    except (AttributeError, ValueError, TypeError):
        return None


def score_stocks(stocks, now):
    peers = {}
    for s in stocks:
        pe = number(s.get("forward_pe"))
        if pe and pe > 0 and s.get("source") == "Yahoo Finance":
            age = age_days(s.get("quote_at"), now)
            if age is not None and 0 <= age <= 5:
                peers.setdefault(s.get("sector"), []).append(pe)
    results = []
    for original in stocks:
        s = dict(original)
        blocked = []
        if s.get("source") != "Yahoo Finance" or s.get("is_mock"):
            blocked.append("실제 수집 데이터가 아님")
        if s.get("currency") != "USD" or s.get("quote_type") != "EQUITY":
            blocked.append("미국 상장 후보군·USD 주식 범위 밖")
        for field, limit, label in [("fetched_at", 2, "수집 시점"), ("quote_at", 5, "가격 시점"), ("financial_at", 150, "최근 분기 기준일")]:
            age = age_days(s.get(field), now)
            if age is None or age < 0 or age > limit:
                blocked.append(f"{label} 누락 또는 오래된 데이터")
        if not s.get("sector") or s.get("sector") in ("Financial Services", "Real Estate"):
            blocked.append("금융·부동산 또는 업종 미확인: 별도 평가모형 필요")
        required = ["price", "market_cap", "revenue_growth", "operating_margin", "fcf", "revenue", "cash", "debt", "ebitda", "forward_pe", "forward_eps", "trailing_eps"]
        missing = [k for k in required if number(s.get(k)) is None]
        s["coverage"] = round(100 * (len(required) - len(missing)) / len(required))
        if missing:
            blocked.append("필수 지표 누락: " + ", ".join(missing))
        s.update(score=None, signals=[], eligible=False, excluded=blocked)
        if blocked:
            results.append(s)
            continue
        if min(s["price"], s["market_cap"], s["revenue"], s["ebitda"], s["forward_pe"], s["forward_eps"], s["trailing_eps"]) <= 0:
            blocked.append("양의 이익·매출·가격 기준 미충족")
            results.append(s)
            continue
        if s["fcf"] <= 0 or s["revenue_growth"] <= 0 or s["operating_margin"] <= 0:
            blocked.append("매출 성장·영업이익률·잉여현금흐름 양수 기준 미충족")
        s["fcf_yield"] = s["fcf"] / s["market_cap"]
        s["net_debt_ebitda"] = (s["debt"] - s["cash"]) / s["ebitda"]
        if s["net_debt_ebitda"] > 3:
            blocked.append("순부채 / EBITDA 3배 초과")
        group = peers.get(s["sector"], [])
        s["peer_pe"] = round(median(group), 2) if len(group) >= 3 else None
        s["peer_count"] = len(group)
        def signal(label, value, maximum, points, evidence):
            s["signals"].append(dict(label=label, value=value, max=maximum, points=points, evidence=evidence))
        g = s["revenue_growth"]
        signal("성장", g, 25, 25 if g >= .15 else 18 if g >= .08 else 10 if g > 0 else 0, f"분기 매출 성장률 YoY {g:.1%}")
        margin = s["operating_margin"]
        signal("수익성", margin, 20, 20 if margin >= .20 else 14 if margin >= .10 else 6 if margin > 0 else 0, f"공급자 영업이익률 {margin:.1%}")
        fy = s["fcf_yield"]
        signal("현금 창출", fy, 20, 20 if fy >= .05 else 14 if fy >= .03 else 7 if fy > 0 else 0, f"공급자 FCF / 시가총액 {fy:.1%}")
        debt = s["net_debt_ebitda"]
        signal("재무 여력", debt, 15, 15 if debt <= 0 else 11 if debt <= 1 else 6 if debt <= 3 else 0, f"순부채 / EBITDA {debt:.2f}배")
        ratio = s["forward_pe"] / s["peer_pe"] if s["peer_pe"] else None
        signal("상대 가격", ratio, 10, 0 if ratio is None else 10 if ratio <= .85 else 7 if ratio <= 1.1 else 3 if ratio <= 1.4 else 0, f"후보군 내 동종 섹터 {len(group)}개 대비 선행 PER" if ratio else "동종 섹터 3개 미만: 평가 보류")
        revision = number(s.get("eps_revision"))
        signal("이익 전망 변화", revision, 10, 0 if revision is None else 10 if revision >= .03 else 6 if revision >= 0 else 0, f"현재 회계연도 EPS 예상치 30일 변화 {revision:.1%}" if revision is not None else "30일 예상치 이력 미확보: 가점 없음")
        s["score"] = sum(x["points"] for x in s["signals"])
        if s["score"] < 65:
            blocked.append("장기 후보 기준 65점 미달")
        s["eligible"] = not blocked
        results.append(s)
    return sorted(results, key=lambda s: (-(s["score"] if s["score"] is not None else -1), s["ticker"]))


def select_week(stocks, history, now):
    """Freeze the first healthy run each ISO week; never revise past snapshots."""
    week = now.strftime("%G-W%V")
    if any(x["week"] == week for x in history):
        return history
    candidates, sectors = [], {}
    for s in stocks:
        if s["eligible"] and sectors.get(s["sector"], 0) < 2:
            candidates.append(s)
            sectors[s["sector"]] = sectors.get(s["sector"], 0) + 1
        if len(candidates) == 3:
            break
    old = history[-1]["picks"] if history else []
    old_tickers = {s["ticker"] for s in old}
    picks = [dict(s, change="유지" if s["ticker"] in old_tickers else "신규") for s in candidates]
    lookup = {s["ticker"]: s for s in stocks}
    removed = []
    for s in old:
        if s["ticker"] not in {p["ticker"] for p in picks}:
            current = lookup.get(s["ticker"])
            reasons = current.get("excluded") if current else ["현재 데이터 수집 실패"]
            removed.append({"ticker": s["ticker"], "reason": " / ".join(reasons or ["상대 순위 또는 섹터 집중 제한"] )})
    return history + [dict(week=week, selected_at=now.isoformat(), model=MODEL, picks=picks, removed=removed)]


def report(s):
    """A factual quantitative dossier, with explicit boundaries on qualitative research."""
    if s["score"] is None:
        return {"thesis": [], "risks": s["excluded"], "scenarios": []}
    risks = ["단일 분기 성장률로 6개월 이상의 성장 지속성을 확정할 수 없습니다.", "경쟁우위·경영진·고객 집중도는 공시 원문 검토가 필요합니다."]
    if s["forward_pe"] > 30:
        risks.append(f"선행 PER {s['forward_pe']:.1f}배: 예상 이익 하향이나 평가배수 축소에 민감합니다.")
    if s["fcf_yield"] < .03:
        risks.append(f"FCF 수익률 {s['fcf_yield']:.1%}: 현재 가격 대비 현금 창출 여유가 작습니다.")
    if s.get("eps_revision") is None:
        risks.append("EPS 전망 수정 이력이 없어 이익 전망 개선 여부를 확인하지 못했습니다.")
    # Sensitivity around current implied forward multiple, not price predictions.
    implied_pe = s["price"] / s["forward_eps"]
    scenarios = []
    for label, eps_factor, pe_factor in [("하락 가정", .8, .8), ("현 수준 유지", 1, 1), ("상승 가정", 1.15, 1.1)]:
        eps, pe = s["forward_eps"] * eps_factor, implied_pe * pe_factor
        price = eps * pe
        scenarios.append(dict(label=label, eps=round(eps, 2), pe=round(pe, 2), price=round(price, 2), change=round((price / s["price"] - 1) * 100, 1)))
    return dict(thesis=[x["evidence"] for x in s["signals"] if x["points"] >= x["max"] * .6], risks=risks, scenarios=scenarios,
                review=["다음 실적에서 매출 성장·영업이익률·FCF의 지속성 확인", "매출 성장률 또는 FCF가 음수로 전환하거나 순부채/EBITDA가 3배를 넘으면 재검토", "경쟁사 대비 차별화와 향후 6~12개월 촉매를 10-K·10-Q 및 IR 자료에서 확인"])
