"""Gmail SMTP 발송 공통 모듈 — 재시도 + 포트 폴백 (2026-11-06).

배경: 11/6 정기 메일이 'Connection unexpectedly closed'(SMTPServerDisconnected)로 실패했는데,
재시도가 없었고 Actions는 continue-on-error 라 '성공'으로만 보였다.

동작: 465(SSL, LOGIN challenge) → 587(STARTTLS) 순서로 시도하고, 전체를 최대 attempts 번 반복(사이 대기 점점 길게).
인증 오류(비밀번호 문제)는 재시도해도 소용없으므로 바로 알린다.
"""
import smtplib
import ssl
import time

HOST = "smtp.gmail.com"


class MailAuthError(Exception):
    """앱 비밀번호가 거부됨 — 재발급·시크릿 갱신이 필요."""


class MailDeliveryUncertain(Exception):
    """전송 중 연결 종료: 서버 접수 여부가 불명확하므로 자동 재발송 금지."""


def _once(sender, password, recipients, message, mode):
    srv = None
    sending = False
    try:
        if mode == "starttls":
            srv = smtplib.SMTP(HOST, 587, timeout=30)
            srv.ehlo()
            srv.starttls(context=ssl.create_default_context())
        else:
            srv = smtplib.SMTP_SSL(HOST, 465, timeout=30, context=ssl.create_default_context())
        srv.ehlo()
        srv.user, srv.password = sender, password
        srv.auth("LOGIN", srv.auth_login, initial_response_ok=False)
        sending = True
        refused = srv.sendmail(sender, recipients, message)
        sending = False
        if refused:
            raise MailDeliveryUncertain("일부 수신자가 거부됨 — 수신자별 확인 후 복구 필요")
    except (smtplib.SMTPServerDisconnected, OSError) as exc:
        if sending:
            raise MailDeliveryUncertain("전송 중 연결 종료 — 보낸편지함 확인 전 재발송 금지") from exc
        raise
    finally:
        if srv:
            try:
                srv.quit()
            except (smtplib.SMTPException, OSError):
                srv.close()  # 전송 접수 후 QUIT 오류 때문에 같은 메일을 다시 보내지 않는다.


def send(sender, password, recipients, message, attempts=3, wait=8, sleep=time.sleep, log=print):
    """성공하면 사용한 방식('starttls'/'ssl')을 돌려주고, 끝내 실패하면 마지막 예외를 그대로 던진다."""
    last = None
    for n in range(1, attempts + 1):
        for mode in ("ssl", "starttls"):
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
