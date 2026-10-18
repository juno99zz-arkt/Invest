"""
주간 메일 리포트 (GitHub Actions 발송, Claude API·Aside 루틴 불필요).
대시보드 생성(generate_invest.py) 직후 index.html 에 주입된 데이터(INJECTED)를 그대로 읽어 작성하므로
메일 내용 = 대시보드 내용.

발송 시점
  --auto  : 월·금요일(KST)이고 오늘 아직 안 보냈으면 발송 (07:00 정기 + 08:00 안전망, 날짜별 1회)
  (매수·매도 신호 수시 메일은 notify.py 가 ntfy 푸시와 함께 보냄)
  --force : 즉시 발송 (수동 실행 mode=report)
  --dry-run : 발송 없이 report_preview.html 저장
환경변수: EMAIL_SENDER, EMAIL_PASSWORD (Gmail 앱 비밀번호), INVEST_REPORT_TO (쉼표 구분 수신자)
"""
import html
import json
import os
import re
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(DATA_DIR, "email_log.json")
DASHBOARD_URL = "https://juno99zz-arkt.github.io/Invest/"
KST = timezone(timedelta(hours=9))
ACTION_COLOR = {"신규편입": "#1a7f37", "유지": "#555", "제외": "#cf222e", "보류": "#9a6700", "미편입": "#888"}
IMPACT_COLOR = {"약화": "#cf222e", "강화": "#1a7f37", "변화 없음": "#555", "해당없음": "#999"}


def e(s):
    return html.escape(str(s if s is not None else ""))


def _env(key):
    return os.environ.get(key, "").replace("\ufeff", "").strip()


def load_injected():
    with open(os.path.join(BASE_DIR, "index.html"), encoding="utf-8") as f:
        m = re.search(r"const INJECTED = (\{.*?\});\n", f.read(), re.S)
    return json.loads(m.group(1))


def _pct(v, d=1):
    return "—" if v is None else f"{v:+.{d}f}%"


def _pc(v):
    return "#888" if v is None else ("#1a7f37" if v >= 0 else "#cf222e")


def _won(n):
    if n is None:
        return "—"
    a = abs(n)
    eok, man = int(a // 1e8), round((a % 1e8) / 1e4)
    s = (f"{eok}억 " if eok else "") + (f"{man:,}만" if man else "") + "원"
    return ("-" if n < 0 else "") + s


def build(today):
    d = load_injected()
    s = d.get("summary") or {}
    lw = s.get("last_week") or {}
    rq = s.get("review_quotes") or {}
    sim = d.get("sim") or {}
    week_now = today.strftime("%G-W%V")
    th = 'style="padding:6px 8px;text-align:left;background:#f3f4f6;font-size:12px"'
    td = 'style="padding:6px 8px;font-size:13px;border-bottom:1px solid #eee;vertical-align:top"'

    stale = ""
    last_d = lw.get("date") or ""
    try:
        age = (today - datetime.strptime(last_d, "%Y-%m-%d").date()).days if last_d else None
    except ValueError:
        age = None
    if age is not None and age > 8:
        stale = ('<div style="font-size:13px;background:#fff8e1;padding:8px 12px;border-radius:6px;margin-bottom:12px">'
                 f'마지막 AI 분석이 {age}일 전({e(last_d)})입니다 — 주간 분석이 반영되지 않았을 수 있습니다. 시세는 매일 갱신됩니다.</div>')
    fgt = ((d.get("m6") or {}).get("fear_tier") or {})
    if fgt.get("score") is not None:
        stale += ('<div style="font-size:13px;background:#f3f4f6;padding:8px 12px;border-radius:6px;margin-bottom:12px">'
                  f'공포·탐욕 지수 {fgt["score"]:.0f} · {e(fgt.get("note"))}</div>')

    # ① 스탠스
    wm = s.get("weekly_message") or {}
    events = "".join(f"<li>{e(x.get('date'))} {e(x.get('event'))}</li>" for x in (wm.get("next_events") or [])[:4])

    # ② 알림
    alerts = [a for a in (d.get("alerts") or []) if a.get("level") in ("high", "mid", "info")][:8]
    alert_html = "".join(
        f"<li><b>{e(a['ticker'])}</b> ({e(a.get('role'))}) {e(a.get('msg'))}</li>" for a in alerts) or "<li>특이 알림 없음</li>"

    # ③ 포트폴리오
    alloc = lw.get("allocation") or (sim.get("allocation") or {})
    port_rows = ""
    for p in s.get("portfolio") or []:
        q = rq.get(p["ticker"]) or {}
        alert = p.get("alert_level") if p.get("alert_level") not in (None, "해당없음") else ""
        price = f"${p['current_price']:.2f}" if p.get("current_price") else "—"
        port_rows += (f"<tr><td {td}><b>{e(p['ticker'])}</b><div style='font-size:11px;color:#888'>{e(p.get('name'))}</div></td>"
                      f"<td {td}>{e(p.get('weight'))}%</td>"
                      f"<td {td}>{e(p.get('action'))}<div style='font-size:11px;color:#9a6700'>{e(alert)}</div></td>"
                      f"<td {td}>{price}</td>"
                      f"<td {td}><span style='color:{_pc(p.get('return_pct'))}'>{_pct(p.get('return_pct'))}</span>"
                      f"<div style='font-size:11px;color:#888'>SPY {_pct(p.get('spy_return_pct'))}</div></td>"
                      f"<td {td}><span style='color:{_pc(q.get('expected_return_pct'))}'>{_pct(q.get('expected_return_pct'))}</span></td></tr>")
    if not port_rows:
        port_rows = f"<tr><td {td} colspan=6>보유 종목 없음 — 전액 원화 현금</td></tr>"

    # ④ 이번 주 결정
    dec_rows = ""
    for x in lw.get("decisions") or []:
        q = rq.get(x["ticker"]) or {}
        r = x.get("reason") or ""
        price = f"${q['price']:.2f}" if q.get("price") else "—"
        bb = f"≤ ${q['buy_below']}" if q.get("buy_below") else "—"
        dec_rows += (f"<tr><td {td}><b>{e(x['ticker'])}</b></td>"
                     f"<td {td}><span style='color:{ACTION_COLOR.get(x['action'], '#555')};white-space:nowrap'>{e(x['action'])}</span></td>"
                     f"<td {td}>{price}<div style='font-size:11px;color:#888'>매수 기준 {bb}</div></td>"
                     f"<td {td}><span style='color:{_pc(q.get('expected_return_pct'))}'>{_pct(q.get('expected_return_pct'))}</span></td>"
                     f"<td {td}><span style='font-size:12px;color:#444'>{e(r[:200])}{'…' if len(r) > 200 else ''}</span></td></tr>")

    # ⑤ 가상 투자
    sim_html = "<p style='font-size:13px;color:#888'>시세 수집 실패로 이번 주 계좌 계산이 없습니다.</p>"
    if sim.get("value_krw"):
        pend = "".join(f"<li>체결 대기: {e(p['signal_date'])} 결정 → 다음 거래일 시가 · "
                       + " · ".join(f"{e(k)} {v}%" for k, v in p["weights"].items()) + "</li>" for p in sim.get("pending") or [])
        trades = "".join(f"<li>{e(t.get('date'))} {e(t.get('side'))} {e(t.get('ticker'))} {t.get('shares')}주 × ${t.get('price_usd')}</li>"
                         for t in (sim.get("trades") or [])[-5:])
        sim_html = (f"<table style='border-collapse:collapse;width:100%'>"
                    f"<tr><td {td}>평가금액</td><td {td}><b>{sim['value_krw']:,}원</b> "
                    f"<span style='color:{_pc(sim.get('return_pct'))}'>({_pct(sim.get('return_pct'), 2)})</span> · 원금 {_won(sim.get('initial_krw'))}</td></tr>"
                    f"<tr><td {td}>같은 비중 SPY</td><td {td}>{_pct(sim.get('bench_return_pct'), 2)}</td></tr>"
                    f"<tr><td {td}>원금 전액 SPY</td><td {td}>{_pct(sim.get('spy_full_return_pct'), 2)}</td></tr>"
                    f"<tr><td {td}>최대 낙폭</td><td {td}>{_pct(sim.get('max_drawdown_pct'), 2)}</td></tr>"
                    f"<tr><td {td}>비중</td><td {td}>개별주 {e(alloc.get('stock_pct'))}% · 원화 현금 {e(alloc.get('cash_pct'))}% · "
                    f"기대수익(12개월) {_pct(alloc.get('expected_return_pct'))}</td></tr></table>"
                    + (f"<ul style='font-size:12px;color:#555;padding-left:18px'>{pend}{trades}</ul>" if pend or trades else ""))

    # ⑥ 뉴스
    order = {"약화": 0, "강화": 1, "변화 없음": 2, "해당없음": 3}
    news = sorted(d.get("news") or [], key=lambda n: (order.get(n.get("thesis_impact"), 4), -(n.get("stars") or 0)))[:5]
    news_html = "".join(
        f"<li style='margin-bottom:8px'><a href='{e(n.get('url'))}'>{e(n.get('title'))}</a> "
        f"<span style='color:#888'>({e(n.get('source'))})</span> "
        f"<b style='color:{IMPACT_COLOR.get(n.get('thesis_impact'), '#555')}'>[{e(n.get('thesis_impact'))}]</b>"
        f"<div style='font-size:12px;color:#444'>{e(n.get('fact') or n.get('summary'))}</div></li>" for n in news)

    added = [x["ticker"] for x in lw.get("decisions") or [] if x["action"] == "신규편입"]
    removed = [x["ticker"] for x in lw.get("decisions") or [] if x["action"] == "제외"]
    quotes_at = s.get("quotes_at") or (d.get("meta") or {}).get("built_at_kst")
    body = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
<body style="font-family:Arial,'Malgun Gothic',sans-serif;color:#1a1a1a;max-width:720px;margin:0 auto;padding:16px">
<h2 style="margin:0 0 4px">AI 투자 브리핑 정기 리포트 ({'월화수목금토일'[today.weekday()]}) · {e(s.get('week'))}</h2>
<div style="color:#888;font-size:13px;margin-bottom:16px">{today.isoformat()} 발송 · {e(lw.get('date'))} 분석 · 시세 {e(quotes_at)} 기준 · <a href="{DASHBOARD_URL}">대시보드 열기</a></div>
{stale}
<h3 style="margin:18px 0 6px">① 시장 스탠스: {e(s.get('stance') or '-')}</h3>
<div style="font-size:13px;color:#444;line-height:1.6">{e(s.get('stance_reason'))}</div>
{('<ul style="font-size:12px;color:#555;padding-left:18px">' + events + '</ul>') if events else ''}

<h3 style="margin:18px 0 6px">② 변경 알림</h3>
<ul style="font-size:13px;padding-left:18px">{alert_html}</ul>

<h3 style="margin:18px 0 6px">③ 추천 포트폴리오 (최대 5종목 + 원화 현금)</h3>
<table style="border-collapse:collapse;width:100%">
<tr><th {th}>종목</th><th {th}>비중</th><th {th}>현재 행동</th><th {th}>현재가</th><th {th}>편입 후</th><th {th}>기대수익</th></tr>
{port_rows}</table>
<div style="font-size:12px;color:#666;margin-top:4px">원화 현금 {e(alloc.get('cash_pct'))}% · {e(alloc.get('reason'))}</div>

<h3 style="margin:18px 0 6px">④ 이번 주 결정 — 신규 {e(', '.join(added) or '없음')} · 제외 {e(', '.join(removed) or '없음')}</h3>
<table style="border-collapse:collapse;width:100%">
<tr><th {th}>종목</th><th {th}>결정</th><th {th}>현재가</th><th {th}>기대수익</th><th {th}>근거</th></tr>
{dec_rows}</table>
<div style="font-size:11px;color:#888;margin-top:4px">기대수익 = 약세 25% · 기준 50% · 강세 25% 시나리오 가중 12개월 (가격 예측 아님)</div>

<h3 style="margin:18px 0 6px">⑤ 가상 투자 계좌</h3>
{sim_html}

<h3 style="margin:18px 0 6px">⑥ 핵심 뉴스 (투자 논리 영향 순)</h3>
<ul style="font-size:13px;padding-left:18px">{news_html}</ul>
<div style="font-size:11px;color:#aaa;margin-top:24px">GitHub Actions 자동 발송 · AI 분석은 Agent(Claude API 미사용) · 투자 판단의 최종 책임은 본인에게 있습니다.</div>
</body></html>"""
    subject = (f"[투자 대시보드] {today.month}/{today.day}({'월화수목금토일'[today.weekday()]}) 정기 리포트 · 스탠스 {s.get('stance') or '-'}"
               f" · 신규 {', '.join(added) or '없음'}" + (f" · 제외 {', '.join(removed)}" if removed else ""))
    return subject, body


def _log():
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"sent": {}}


def main():
    now = datetime.now(KST)
    key = now.strftime("%Y-%m-%d")
    log = _log()
    if "--auto" in sys.argv:
        if now.weekday() not in (0, 4):
            print(f"오늘은 월·금요일이 아님({now:%a}) — 정기 메일 건너뜀")
            return
        if key in log.get("sent", {}):
            print(f"{key} 정기 메일은 이미 발송됨({log['sent'][key]}) — 건너뜀")
            return
    subject, body = build(now.date())
    if "--dry-run" in sys.argv:
        out = os.path.join(BASE_DIR, "report_preview.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(body)
        print(subject, "→", out)
        return
    sender, password = _env("EMAIL_SENDER"), _env("EMAIL_PASSWORD").replace(" ", "")
    recipients = [r.strip() for r in _env("INVEST_REPORT_TO").split(",") if r.strip()]
    if not (sender and password and recipients):
        print("::warning::메일 설정(EMAIL_SENDER / EMAIL_PASSWORD / INVEST_REPORT_TO) 없음 — 발송 건너뜀")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, sender, ", ".join(recipients)
    msg.attach(MIMEText(body, "html", "utf-8"))
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as srv:
        srv.starttls()
        srv.login(sender, password)
        srv.sendmail(sender, recipients, msg.as_string())
    log.setdefault("sent", {})[key] = now.strftime("%Y-%m-%d %H:%M")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    print(f"리포트 발송 완료 → {len(recipients)}명: {subject}")


if __name__ == "__main__":
    main()
