"""
매수·매도 신호 수시 알림 — 메일(EMAIL_SENDER→INVEST_REPORT_TO) + 휴대폰 푸시 (ntfy.sh — 무료, 계정 불필요, 휴대폰 ntfy 앱에서 토픽 구독).
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


def agent_signals(hist, since=""):
    """주간 분석·중간 재평가에서 확정된 매도(제외·비중 축소)와 매수(신규 편입·비중 확대). since 이후 결정만."""
    out = []
    weeks = sorted(hist.get("weeks", []), key=lambda w: (w["date"], w.get("interim", False)))
    for i, w in enumerate(weeks):
        prev = next((x.get("weights") for x in reversed(weeks[:i]) if x.get("weights")), None) or {}
        cur = w.get("weights") or {}
        label = w.get("week")
        if w["date"] < since:
            continue
        added = [d["ticker"] for d in w.get("decisions", []) if d["action"] == "신규편입"]
        for d in w.get("decisions", []):
            if d["action"] == "신규편입" and cur.get(d["ticker"]):
                out.append({"key": f"{label}:{d['ticker']}:편입", "level": "buy_exec", "ticker": d["ticker"],
                            "title": f"[매수] {d['ticker']} 신규 편입 {cur[d['ticker']]}%",
                            "msg": f"{w['date']} {label} 판단: 비중 {cur[d['ticker']]}%로 신규 매수 (다음 거래일 시가 기준)\n{d['reason'][:300]}"})
        if w.get("weights") is not None:
            for tk, nw in cur.items():
                pw = prev.get(tk)
                if pw is not None and nw > pw and tk not in added:
                    reason = next((d["reason"] for d in w.get("decisions", []) if d["ticker"] == tk), "")
                    out.append({"key": f"{label}:{tk}:확대:{nw}", "level": "buy_exec", "ticker": tk,
                                "title": f"[매수] {tk} 비중 확대 {pw}% → {nw}%",
                                "msg": f"{w['date']} {label} 판단: 비중 {pw}% → {nw}% (차액 추가 매수)\n{reason[:300]}"})
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


def fear_signals():
    """공포·탐욕 20/10/5 하향 돌파 → [매수 신호] (단계마다 돌파 1회당 1번). 대시보드 생성 직후 index.html 의 후보 목록 사용."""
    import re
    try:
        with open(os.path.join(BASE_DIR, "index.html"), encoding="utf-8") as f:
            inj = json.loads(re.search(r"const INJECTED = (\{.*?\});\n", f.read(), re.S).group(1))
    except Exception as e:
        print("::warning::index.html 읽기 실패:", e)
        return []
    m6 = inj.get("m6") or {}
    t = m6.get("fear_tier") or {}
    if not t.get("tier") and t.get("watch"):  # 20 하향: 매수 가중 없이 경계만 (키 형식 동일 → 같은 돌파는 1회)
        return [{"key": f"fg:{t['watch_level']}:{t.get('watch_crossed')}", "level": "warn", "ticker": "시장",
                 "title": f"[공포 경계] 공포·탐욕 {t['low']:.0f} — {t['watch_level']} 하향, 10 접근 경계",
                 "msg": t.get("note", "") + "\n\n매수 규칙은 바뀜지 않습니다. 10 미만으로 내려가면 [매수 신호]를 보냅니다."}]
    if not t.get("tier"):
        return []
    cands = [c for c in (m6.get("fear_candidates") or []) if c.get("eligible")]
    near = [c for c in (m6.get("fear_candidates") or []) if not c.get("eligible") and c.get("gap_pct", 99) <= 10][:4]
    line = lambda c: (f"{c['ticker']} ${c['price']:.2f} (기준 ${c['buy_below']}, {c['gap_pct']:+.1f}%, 기대수익 "
                      f"{c['expected_return_pct']:+.0f}%) {c['kind']}" if c.get("expected_return_pct") is not None else c["ticker"])
    msg = (t.get("note", "") + "\n\n지금 가격으로 조건 충족: " + ("\n· " + "\n· ".join(map(line, cands)) if cands else "없음")
           + ("\n매수 기준가 10% 이내: " + ", ".join(f"{c['ticker']} {c['gap_pct']:+.0f}%" for c in near) if near else "")
           + "\n\n지수만으로 사지 않습니다 — 다음 아침 Agent 가 후보를 재평가하고, 조건을 통과한 종목만 편입·추가 매수합니다.")
    return [{"key": f"fg:{t['level']}:{t.get('crossed')}", "level": "buy", "ticker": "시장",
             "title": f"[매수 신호] 공포·탐욕 {t['low']:.0f} — {t['level']} 하향 돌파 ({t['name']})", "msg": msg}]


def send_email(sigs):
    """이번 실행에서 새로 생긴 매수·매도 신호를 메일 1통으로 (정기 리포트와 같은 발신·수신자)."""
    import html as _h
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    env = lambda k: os.environ.get(k, "").replace("\ufeff", "").strip()
    sender, pw = env("EMAIL_SENDER"), env("EMAIL_PASSWORD").replace(" ", "")
    to = [r.strip() for r in env("INVEST_REPORT_TO").split(",") if r.strip()]
    if not (sender and pw and to and sigs):
        if sigs:
            print("::warning::메일 설정 없음 — 수시 메일 건너뜀")
        return False
    color = {"sell": "#cf222e", "warn": "#9a6700", "buy": "#1a7f37", "buy_exec": "#1a7f37"}
    order = {"sell": 0, "buy_exec": 1, "buy": 2, "warn": 3}
    sigs = sorted(sigs, key=lambda s: order.get(s["level"], 9))
    rows = "".join(
        f'<div style="border-left:4px solid {color.get(s["level"], "#555")};padding:8px 12px;margin:10px 0;background:#fafafa">'
        f'<div style="font-weight:700;color:{color.get(s["level"], "#555")}">{_h.escape(s["title"])}</div>'
        f'<div style="font-size:13px;color:#333;line-height:1.6;margin-top:4px">{_h.escape(s["msg"]).replace(chr(10), "<br>")}</div></div>'
        for s in sigs)
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    body = (f'<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="font-family:Arial,\'Malgun Gothic\',sans-serif;'
            f'max-width:680px;margin:0 auto;padding:16px"><h2 style="margin:0 0 4px">투자 대시보드 수시 알림</h2>'
            f'<div style="color:#888;font-size:13px">{now} KST · <a href="{DASHBOARD_URL}">대시보드 열기</a></div>{rows}'
            '<div style="font-size:11px;color:#aaa;margin-top:20px">GitHub Actions 자동 발송 (ntfy 푸시와 동시) · '
            '가상 계좌 기준이며 투자 판단의 최종 책임은 본인에게 있습니다.</div></body></html>')
    subject = "[투자 알림] " + sigs[0]["title"] + (f" 외 {len(sigs) - 1}건" if len(sigs) > 1 else "")
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, sender, ", ".join(to)
    msg.attach(MIMEText(body, "html", "utf-8"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as srv:
            srv.starttls()
            srv.login(sender, pw)
            srv.sendmail(sender, to, msg.as_string())
    except Exception as e:
        print("::warning::수시 메일 실패:", e)
        return False
    print(f"수시 메일 발송 → {len(to)}명: {subject}")
    return True


def main():
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    if "--test" in sys.argv:
        t = {"title": "[테스트] AI 투자 브리핑 알림 연결됨", "level": "buy",
             "msg": f"{now} · 매수·매도 신호가 생기면 이렇게 메일과 푸시로 동시에 알려드립니다."}
        send(t["title"], t["msg"], priority=3, tags=["white_check_mark"])
        if "--mail" in sys.argv:
            send_email([t])
        return
    hist = _load(os.path.join(DATA_DIR, "picks_history.json"), {})
    log = _load(LOG_PATH, {"sent": {}})
    sent = log.setdefault("sent", {})
    first_run = not sent and "--prices" not in sys.argv
    # 매수·매도 결정 알림은 이 기능을 켠 날 이후 결정부터 (과거 이력을 한꺼번에 보내지 않기 위해)
    since = log.setdefault("agent_since", now[:10])
    sigs = [] if "--prices" in sys.argv else agent_signals(hist, since)
    try:
        sigs += price_signals(hist)
    except Exception as e:
        print("::warning::가격 점검 실패:", e)
    if "--prices" not in sys.argv:
        sigs += fear_signals()
    new = [s for s in sigs if s["key"] not in sent]
    if first_run:
        # 처음 켤 때 과거 이력은 보내지 않고 기록만 (오늘 이후 신호부터 푸시)
        for s in new:
            if s["level"] == "sell":
                sent[s["key"]] = now + " (초기화)"
        new = [s for s in new if s["level"] != "sell"]
    pushed = []
    for s in new:
        ok = send(s["title"], s["msg"], priority=5 if s["level"] in ("sell", "buy", "buy_exec") else 4,
                  tags={"sell": ["rotating_light"], "buy": ["moneybag"], "buy_exec": ["chart_with_upwards_trend"]}.get(s["level"], ["warning"]))
        pushed.append((s, ok))
    mailed = send_email(new) if new else False
    for s, ok in pushed:
        if ok or mailed:
            sent[s["key"]] = now + (" 푸시" if ok else "") + (" 메일" if mailed else "")
    if not new:
        print("새 매수·매도 신호 없음")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
