"""
매도 신호 휴대폰 푸시 (ntfy.sh — 무료, 계정 불필요, 휴대폰 ntfy 앱에서 토픽 구독).
GitHub Actions 에서 실행:
  python notify.py            : 전체 점검 (Agent 판단 매도 + 가격 경고)  — 매일 06:00, finalize 직후
  python notify.py --prices   : 가격 경고만 (미국 장중 30분마다)
  python notify.py --test     : 테스트 푸시 1건
환경변수: NTFY_TOPIC (GitHub 시크릿 — 공개 저장소라 코드에 넣지 않음), NTFY_SERVER(선택, 기본 https://ntfy.sh)

매도 신호
  [매도]     Agent 판단: 보유 종목 '제외'(논리 붕괴·부적합) 또는 비중 축소 (주간 분석·중간 재평가 반영 시)
  [매도 경고] 가격: 보유 종목이 약세 시나리오 가격 이하 / 분석 시점 대비 −10% 이상 / 편입가 대비 −15% 이상
             → 다음 날 아침 Agent 가 해당 종목을 재평가해 매도 여부를 확정 (확정되면 [매도] 푸시)
같은 신호는 한 번만 보낸다 (data/push_log.json).
"""
import glob
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(DATA_DIR, "push_log.json")
DASHBOARD_URL = "https://juno99zz-arkt.github.io/Invest/"
KST = timezone(timedelta(hours=9))
DROP_FROM_ANALYSIS = -10.0
DROP_FROM_ADDED = -15.0


def _load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def send(title, message, priority=4, tags=None):
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        print("::warning::NTFY_TOPIC 시크릿 없음 — 푸시 건너뜀:", title)
        return False
    server = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
    body = json.dumps({"topic": topic, "title": title, "message": message, "priority": priority,
                       "tags": tags or [], "click": DASHBOARD_URL}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(server + "/", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            ok = 200 <= r.status < 300
    except Exception as e:
        print("::warning::푸시 실패:", e)
        return False
    print(("푸시 발송: " if ok else "푸시 실패: ") + title)
    return ok


def agent_signals(hist):
    """주간 분석·중간 재평가에서 확정된 매도(제외)·비중 축소."""
    out = []
    weeks = sorted(hist.get("weeks", []), key=lambda w: (w["date"], w.get("interim", False)))
    for i, w in enumerate(weeks):
        prev = next((x.get("weights") for x in reversed(weeks[:i]) if x.get("weights")), None) or {}
        cur = w.get("weights") or {}
        label = w.get("week")
        for d in w.get("decisions", []):
            if d["action"] == "제외":
                out.append({"key": f"{label}:{d['ticker']}:제외", "level": "sell", "ticker": d["ticker"],
                            "title": f"[매도] {d['ticker']} 전량 매도",
                            "msg": f"{w['date']} {label} 판단: 투자 논리 붕괴·부적합 → 포트폴리오에서 제외\n{d['reason'][:300]}"})
        if w.get("weights") is not None:
            for tk, pw in prev.items():
                nw = cur.get(tk, 0)
                if nw < pw and tk not in [d["ticker"] for d in w.get("decisions", []) if d["action"] == "제외"]:
                    reason = next((d["reason"] for d in w.get("decisions", []) if d["ticker"] == tk), "")
                    out.append({"key": f"{label}:{tk}:축소:{nw}", "level": "sell", "ticker": tk,
                                "title": f"[매도] {tk} 비중 축소 {pw}% → {nw}%",
                                "msg": f"{w['date']} {label} 판단: 비중 {pw}% → {nw}% (차액 매도)\n{reason[:300]}"})
    return out


def price_signals(hist):
    """보유 종목 가격 경고 (AI 없이 매일·장중 점검)."""
    held = hist.get("portfolio", [])
    if not held:
        return []
    reports = sorted(glob.glob(os.path.join(DATA_DIR, "reports", "*.json")))
    rep = _load(reports[-1], {}) if reports else {}
    from data_fetcher import fetch_prices
    prices = fetch_prices([h["ticker"] for h in held])
    out = []
    for h in held:
        tk, p = h["ticker"], prices.get(h["ticker"])
        if not p:
            continue
        an = (rep.get("analyses") or {}).get(tk) or {}
        a, m = an.get("analysis") or {}, an.get("metrics") or {}
        d0 = an.get("interim_update") or rep.get("date") or ""
        dt = a.get("decision_table") or {}
        bear = next((s for s in dt.get("scenarios", []) if s.get("name") == "약세"), None)
        base = f"현재가 ${p:.2f} · 비중 {h.get('weight', '—')}%"
        if bear and bear.get("price") and p <= bear["price"]:
            out.append({"key": f"{tk}:약세도달:{d0}", "level": "warn", "ticker": tk,
                        "title": f"[매도 경고] {tk} 약세 시나리오 가격 도달",
                        "msg": f"{base} ≤ 약세 시나리오 ${bear['price']}\n가정: {bear.get('assumption', '')[:200]}\n"
                               "다음 아침 Agent 가 재평가해 매도 여부를 확정합니다."})
        a0 = m.get("price")
        if a0 and (p / a0 - 1) * 100 <= DROP_FROM_ANALYSIS:
            out.append({"key": f"{tk}:급락:{d0}", "level": "warn", "ticker": tk,
                        "title": f"[매도 경고] {tk} 분석 후 {(p / a0 - 1) * 100:.0f}%",
                        "msg": f"{base} (분석 시 ${a0:.2f}, {d0})\n판단 변경 조건 점검 필요 — 다음 아침 Agent 재평가."})
        ap = h.get("added_price")
        if ap and (p / ap - 1) * 100 <= DROP_FROM_ADDED:
            out.append({"key": f"{tk}:편입가하락:{h.get('added_date')}", "level": "warn", "ticker": tk,
                        "title": f"[매도 경고] {tk} 편입가 대비 {(p / ap - 1) * 100:.0f}%",
                        "msg": f"{base} (편입 {h.get('added_date')} ${ap:.2f})\n주가 하락만으로 팔지 않지만 논리 점검 대상입니다."})
    return out


def main():
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    if "--test" in sys.argv:
        send("[테스트] AI 투자 브리핑 알림 연결됨",
             f"{now} · 매도 신호가 생기면 이렇게 알려드립니다. 누르면 대시보드가 열립니다.", priority=3, tags=["white_check_mark"])
        return
    hist = _load(os.path.join(DATA_DIR, "picks_history.json"), {})
    log = _load(LOG_PATH, {"sent": {}})
    sent = log.setdefault("sent", {})
    first_run = not sent and "--prices" not in sys.argv
    sigs = [] if "--prices" in sys.argv else agent_signals(hist)
    try:
        sigs += price_signals(hist)
    except Exception as e:
        print("::warning::가격 점검 실패:", e)
    new = [s for s in sigs if s["key"] not in sent]
    if first_run:
        # 처음 켤 때 과거 이력은 보내지 않고 기록만 (오늘 이후 신호부터 푸시)
        for s in new:
            if s["level"] == "sell":
                sent[s["key"]] = now + " (초기화)"
        new = [s for s in new if s["level"] != "sell"]
    for s in new:
        ok = send(s["title"], s["msg"], priority=5 if s["level"] == "sell" else 4,
                  tags=["rotating_light"] if s["level"] == "sell" else ["warning"])
        if ok:
            sent[s["key"]] = now
    if not new:
        print("새 매도 신호 없음")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
