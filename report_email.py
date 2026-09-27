"""
격주 파이프라인 결과 메일 리포트 (GitHub Actions, run_weekly.py 직후).
- 이번 회차 Claude 비용 (지난 회차 대비, 캐시 적중률·검색 횟수)
- 편입/유지/제외 결정, 시장 스탠스, 핵심 뉴스
수동 발송: python report_email.py --latest (가장 최근 리포트 기준)
환경변수: EMAIL_SENDER, EMAIL_PASSWORD (Gmail 앱 비밀번호), INVEST_REPORT_TO (쉼표 구분 수신자)
"""
import glob
import html
import json
import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DASHBOARD_URL = "https://juno99zz-arkt.github.io/Invest/"
KST = timezone(timedelta(hours=9))
ACTION_COLOR = {"신규편입": "#1a7f37", "유지": "#555", "제외": "#cf222e", "보류": "#9a6700", "미편입": "#888"}


def _env(key):
    return os.environ.get(key, "").replace("﻿", "").strip()


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _usage_total(report):
    """리포트의 모델별 사용량 합계 (옛 리포트엔 캐시 항목 없음)."""
    tot = {}
    for u in (report or {}).get("usage", {}).values():
        for k, v in u.items():
            if isinstance(v, (int, float)):
                tot[k] = tot.get(k, 0) + v
    return tot


def _row(label, cur, prev, fmt="{:,}", lower_is_better=True):
    diff = ""
    if prev:
        pct = (cur / prev - 1) * 100
        good = pct < 0 if lower_is_better else pct > 0
        color = "#1a7f37" if good else "#cf222e"
        diff = f'<span style="color:{color}">{pct:+.0f}%</span>'
    prev_s = fmt.format(prev) if prev else "-"
    return (f'<tr><td style="padding:6px 10px">{label}</td><td style="padding:6px 10px;text-align:right">{fmt.format(cur)}</td>'
            f'<td style="padding:6px 10px;text-align:right;color:#888">{prev_s}</td><td style="padding:6px 10px;text-align:right">{diff}</td></tr>')


def build(today, latest=False):
    """latest=True: 날짜와 무관하게 가장 최근 리포트로 작성 (수동 발송)."""
    reports = sorted(glob.glob(os.path.join(DATA_DIR, "reports", "*.json")))
    cur = _load(reports[-1]) if reports else None
    if not cur or (not latest and cur.get("date") != today):
        return (f"[투자 대시보드] {today} 격주 분석 실패/건너뜀",
                "<p>이번 격주 실행에서 새 리포트가 생성되지 않았습니다 (Claude API 키·요청 오류 가능). "
                "GitHub Actions 로그를 확인하세요.</p>")
    prev = _load(reports[-2]) if len(reports) > 1 else None
    signals = _load(os.path.join(DATA_DIR, "weekly_signals.json"))
    brief = signals.get("market_brief") or {}

    u, pu = _usage_total(cur), _usage_total(prev)
    hit = (f"{u['cache_read_tokens'] / u['input_tokens'] * 100:.0f}%"
           if "cache_read_tokens" in u and u.get("input_tokens") else "-")
    cost_rows = "".join([
        _row("추정 비용 (USD)", u.get("est_cost_usd", 0), pu.get("est_cost_usd"), "${:,.2f}"),
        _row("호출 수", u.get("calls", 0), pu.get("calls")),
        _row("입력 토큰", u.get("input_tokens", 0), pu.get("input_tokens")),
        _row("출력 토큰", u.get("output_tokens", 0), pu.get("output_tokens")),
        _row("웹검색", u.get("web_searches", 0), pu.get("web_searches")),
    ])
    fresh = sum(1 for c in cur.get("candidates", []) if c.get("analysis") != "재사용")
    reused = len(cur.get("candidates", [])) - fresh

    names = {tk: (a.get("metrics") or {}).get("name") or "" for tk, a in cur.get("analyses", {}).items()}
    dec_rows = "".join(
        f'<tr><td style="padding:6px 10px;font-weight:700">{html.escape(d["ticker"])}'
        f'<div style="font-weight:400;font-size:11px;color:#888">{html.escape(names.get(d["ticker"], ""))}</div></td>'
        f'<td style="padding:6px 10px;color:{ACTION_COLOR.get(d["action"], "#555")};white-space:nowrap">{html.escape(d["action"])}</td>'
        f'<td style="padding:6px 10px;font-size:12px;color:#444">{html.escape(d["reason"][:220])}{"…" if len(d["reason"]) > 220 else ""}</td></tr>'
        for d in cur.get("decisions", []))

    news = "".join(
        f'<li style="margin-bottom:6px"><a href="{html.escape(n["url"])}">{html.escape(n["title"])}</a> '
        f'<span style="color:#888">({html.escape(n.get("source", ""))}, {"★" * n.get("stars", 0)})</span></li>'
        for n in sorted(brief.get("news", []), key=lambda n: -n.get("stars", 0))[:5])
    news_src = {"rss": "RSS 후보에서 선별", "web_search": "웹검색 (RSS 부족 시 대체)"}.get(brief.get("news_source"), "-")

    th = 'style="padding:6px 10px;text-align:left;background:#f5f5f5"'
    body = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;color:#1a1a1a;max-width:680px;margin:0 auto;padding:16px">
<h2 style="margin:0 0 4px">투자 대시보드 격주 리포트 · {cur['week']}</h2>
<div style="color:#888;font-size:13px;margin-bottom:16px">{today} 실행 · <a href="{DASHBOARD_URL}">대시보드 열기</a></div>

<h3 style="margin:20px 0 8px">① Claude 비용</h3>
<table style="border-collapse:collapse;font-size:13px;width:100%">
<tr><th {th}>항목</th><th {th}>이번 회차</th><th {th}>지난 회차 ({prev['week'] if prev else '-'})</th><th {th}>변화</th></tr>
{cost_rows}</table>
<div style="font-size:12px;color:#666;margin-top:6px">캐시 적중률 {hit} · 종목 분석 {fresh}건 신규 / {reused}건 재사용 · 뉴스 {news_src}</div>

<h3 style="margin:20px 0 8px">② 시장 스탠스: {html.escape(brief.get('stance', '-'))}</h3>
<div style="font-size:13px;color:#444">{html.escape(brief.get('stance_reason', ''))}</div>

<h3 style="margin:20px 0 8px">③ 편입·유지·제외 결정</h3>
<table style="border-collapse:collapse;width:100%">
<tr><th {th}>종목</th><th {th}>결정</th><th {th}>근거</th></tr>
{dec_rows}</table>

<h3 style="margin:20px 0 8px">④ 핵심 뉴스 Top 5</h3>
<ul style="font-size:13px;padding-left:18px">{news}</ul>
<div style="font-size:11px;color:#aaa;margin-top:24px">자동 발송 · 투자 판단의 최종 책임은 본인에게 있습니다.</div>
</body></html>"""
    subject = f"[투자 대시보드] {cur['week']} 격주 리포트 · 비용 ${u.get('est_cost_usd', 0):.2f}"
    return subject, body


def main():
    sender, password = _env("EMAIL_SENDER"), _env("EMAIL_PASSWORD").replace(" ", "")
    recipients = [r.strip() for r in _env("INVEST_REPORT_TO").split(",") if r.strip()]
    today = datetime.now(KST).date().isoformat()
    subject, body = build(today, latest="--latest" in sys.argv)
    if "--dry-run" in sys.argv:
        out = os.path.join(BASE_DIR, "report_preview.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(body)
        print(subject, "→", out)
        return
    if not (sender and password and recipients):
        print("::warning::메일 설정(EMAIL_SENDER / EMAIL_PASSWORD / INVEST_REPORT_TO) 없음 — 리포트 발송 건너뜀")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, sender, ", ".join(recipients)
    msg.attach(MIMEText(body, "html", "utf-8"))
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as srv:
        srv.starttls()
        srv.login(sender, password)
        srv.sendmail(sender, recipients, msg.as_string())
    print(f"리포트 발송 완료 → {len(recipients)}명")


if __name__ == "__main__":
    main()
