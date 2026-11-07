"""Gmail SMTP 발송 공통 모듈 — 재시도 + 포트 폴백 (2026-11-06).

배경: 11/6 정기 메일이 'Connection unexpectedly closed'(SMTPServerDisconnected)로 실패했는데,
재시도가 없었고 Actions는 continue-on-error 라 '성공'으로만 보였다.

동작: 587(STARTTLS) → 465(SSL) 순서로 시도하고, 전체를 최대 attempts 번 반복(사이 대기 점점 길게).
인증 오류(비밀번호 문제)는 재시도해도 소용없으므로 바로 알린다.
"""
import smtplib
import ssl
import time

HOST = "smtp.gmail.com"


class MailAuthError(Exception):
    """앱 비밀번호가 거부됨 — 재발급·시크릿 갱신이 필요."""


def _once(sender, password, recipients, message, mode):
    if mode == "starttls":
        with smtplib.SMTP(HOST, 587, timeout=30) as srv:
            srv.ehlo()
            srv.starttls(context=ssl.create_default_context())
            srv.ehlo()
            srv.login(sender, password)
            srv.sendmail(sender, recipients, message)
    else:
        with smtplib.SMTP_SSL(HOST, 465, timeout=30, context=ssl.create_default_context()) as srv:
            srv.login(sender, password)
            srv.sendmail(sender, recipients, message)


def send(sender, password, recipients, message, attempts=3, wait=8, sleep=time.sleep, log=print):
    """성공하면 사용한 방식('starttls'/'ssl')을 돌려주고, 끝내 실패하면 마지막 예외를 그대로 던진다."""
    last = None
    for n in range(1, attempts + 1):
        for mode in ("starttls", "ssl"):
            try:
                _once(sender, password, recipients, message, mode)
                if n > 1 or mode != "starttls":
                    log(f"메일 발송 성공 (시도 {n}회차, 방식 {mode})")
                return mode
            except smtplib.SMTPAuthenticationError as e:
                # 535 등: 비밀번호 거부. 재시도 무의미.
                raise MailAuthError(f"Gmail 로그인 거부({e.smtp_code}) — 앱 비밀번호 재발급 필요: {e.smtp_error!r}") from e
            except (smtplib.SMTPException, OSError, ssl.SSLError) as e:
                last = e
                log(f"::warning::메일 시도 {n}회차 {mode} 실패: {type(e).__name__}: {e}")
        if n < attempts:
            sleep(wait * n)
    raise last
