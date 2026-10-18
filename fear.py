"""
공포·탐욕 지수(CNN Fear & Greed) 단계 → 매수 신호 가중치.

단계는 '최근 N거래일(기본 5) 최저치' 기준: 10 / 5 를 하향 돌파하면 2 / 3 단계 (매수 가중).
20 하향은 2016~2026 QQQ 백테스트상 평소와 차이가 없어 가중치 없이 경계 알림만 (watch).
3단계(5)는 매수 후 추가 하락(평균 −7.9%, 최악 −15.8%)에 대비해 늘릴 비중의 절반씩 분할 매수.
(극단적 공포는 며칠 만에 지나가는 경우가 많아, 토요일 판단 시점에 회복했더라도 그 주에 돌파했으면 반영)

지수는 '전부'가 아니다 — 단계가 바꾸는 것은 규칙의 문턱뿐이고, 다음 안전장치는 그대로다:
  편입 적합/검증 완료 요구, 논리 붕괴·부적합 제외, '추가 매수 중단'·'비중 재검토' 경고, 검증 대기,
  약세 시 종목당 전체 손실 한도, 한 종목·테마 상한, 최대 5종목.
수집 실패 시 0단계(가중치 없음)로 안전하게 동작.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BASE_DIR, "data", "fear_greed.json")

DEFAULT_TIERS = [
    # 20: 2016~2026 QQQ 백테스트상 단독 매수 근거 없음 → 가중치 없이 '10 접근 경계' 알림만 (2026-10-18 사용자 승인)
    {"level": 20, "name": "극단적 공포", "alert_only": True},
    {"level": 10, "name": "패닉", "stock_cap_add": 20, "hurdle_pct": 6, "buy_below_tolerance_pct": 6,
     "starter_weight": 15, "allow_watch": True, "add_to_holdings_pct": 5, "max_fear_picks": 2},
    {"level": 5, "name": "투매", "stock_cap_add": 30, "hurdle_pct": 4, "buy_below_tolerance_pct": 10,
     "starter_weight": 15, "conviction4_weight": 25, "allow_watch": True, "add_to_holdings_pct": 10,
     "max_fear_picks": 3, "staged_buy": True},
]


def _profile():
    try:
        with open(os.path.join(BASE_DIR, "data", "risk_profile.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load(fresh=True):
    """최신 지수 dict (data_fetcher.fetch_fear_greed 형식). 실패 시 마지막 저장본, 그것도 없으면 None."""
    fg = None
    if fresh:
        try:
            from data_fetcher import fetch_fear_greed
            fg = fetch_fear_greed()
        except Exception as e:
            print(f"공포·탐욕 지수 수집 실패: {e}")
    if fg:
        try:
            os.makedirs(os.path.dirname(CACHE), exist_ok=True)
            with open(CACHE, "w", encoding="utf-8") as f:
                json.dump(fg, f, ensure_ascii=False)
        except Exception:
            pass
        return fg
    try:
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def crossed_on(fg, level):
    """가장 최근에 level 을 하향 돌파한 날짜 (이력 기준)."""
    h = (fg or {}).get("history") or []
    for i in range(len(h) - 1, 0, -1):
        if h[i]["v"] < level <= h[i - 1]["v"]:
            return h[i]["d"]
    return h[0]["d"] if h and h[0]["v"] < level else None


def tier(fg=None, profile=None):
    """→ {"tier": 0~3, "score", "low", "level", "name", "crossed", 규칙값...}. 0단계면 가중치 없음."""
    prof = (profile or _profile()).get("fear_greed_boost") or {}
    tiers = sorted(prof.get("tiers") or DEFAULT_TIERS, key=lambda t: -t["level"])
    n = int(prof.get("lookback_days", 5))
    if fg is None:
        fg = load(fresh=False)
    if not fg or fg.get("score") is None:
        return {"tier": 0, "score": None, "low": None, "note": "공포·탐욕 지수 없음 — 가중치 미적용"}
    recent = [p["v"] for p in (fg.get("history") or [])[-n:]] + [fg["score"]]
    low = min(recent)
    out = {"tier": 0, "score": fg["score"], "low": round(low, 1), "lookback_days": n, "as_of": fg.get("as_of")}
    for i, t in enumerate(tiers, 1):
        if low < t["level"]:
            if t.get("alert_only"):  # 가중치 없이 경계 알림만 (tier 는 0 유지)
                out.update({"watch": True, "watch_level": t["level"], "watch_name": t["name"],
                            "watch_crossed": crossed_on(fg, t["level"])})
            else:
                out.update({"tier": i, **t, "crossed": crossed_on(fg, t["level"])})
    if not out["tier"] and out.get("watch"):
        out["note"] = (f"공포·탐욕 최근 {n}일 최저 {low:.0f} → {out['watch_level']} 하향({out['watch_name']}) — "
                       f"10년 백테스트상 단독 매수 근거가 없어 매수 가중 없음. 10 미만으로 내려가면 매수 가중 시작 (10 접근 경계)")
        return out
    if out["tier"]:
        out["note"] = (f"공포·탐욕 최근 {n}일 최저 {low:.0f} → {out['level']} 하향 돌파({out['name']}, {out['tier']}단계): "
                       f"주식 상한 +{out['stock_cap_add']}%p · 최소 기대수익 {out['hurdle_pct']}% · "
                       f"매수 기준가 +{out['buy_below_tolerance_pct']}% 허용"
                       + (" · 관찰 종목도 매수 기준가 이하면 탐색 편입" if out.get("allow_watch") else "")
                       + (f" · 보유 종목 +{out['add_to_holdings_pct']}%p 추가 매수 허용" if out.get("add_to_holdings_pct") else "")
                       + (" · 추가 하락 위험 대비 분할 매수(늘릴 비중의 절반씩, 2~3회)" if out.get("staged_buy") else ""))
    else:
        out["note"] = f"공포·탐욕 최근 {n}일 최저 {low:.0f} — 매수 가중 없음 (10 미만부터 적용)"
    return out
