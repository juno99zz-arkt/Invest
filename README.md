# Invest — AI 투자 브리핑 대시보드 (Claude API 비용 0원)

대시보드: https://juno99zz-arkt.github.io/Invest/

정량 데이터 수집·결정·배포·메일은 GitHub Actions(무료)가, 웹검색 기반 시장 브리핑과 종목 심층분석은 **Agent**가 수행합니다.
Claude API(ANTHROPIC_API_KEY)는 더 이상 쓰지 않습니다.

## 주간 흐름

| 시각 (KST) | 주체 | 내용 |
|---|---|---|
| 토 09:00 | Actions `prepare` | 유니버스 정량 점수·신호 → 후보 선정 → `data/pending/request.json` (분석 요청서) |
| 토 오전 | Agent | 요청서를 읽고 시장 브리핑(스탠스·뉴스·일정) + 종목 심층분석(판단표·데이터 검증) → `data/aside/result.json` 업로드 |
| 업로드 직후 | Actions `finalize` | 결과 검증 → 편입·유지·제외 결정 → 비중 → 이력·리포트 → 대시보드 배포 → **주간 메일 발송** |
| 토 21:00 | Actions `report` 안전망 | 그 주 메일이 아직 안 나갔으면 현재 대시보드 기준으로 발송 |
| 수 | Agent (알림 있을 때만) | 보유·관심 종목 중간 재평가 (`mode: interim`) |
| 매일 17:00 | Actions `daily` | 시세·PEG·상위 50 갱신, 변경 알림 |

## 계좌 규칙 (`data/risk_profile.json`)
최대 5종목 개별주 + 원화 현금 (ETF 없음). 확신도·기대수익(약세25·기준50·강세25)·약세 시 종목당 전체 손실 한도로 종목 비중,
시장 스탠스별 개별주 합계 상한, 나머지 현금. 가상 투자 시뮬레이션(원금 1억원)은 다음 거래일 시가 체결·비용·배당·현금이자 반영.

## 주간 메일
`report_email.py` — 대시보드에 주입된 데이터 그대로 (스탠스, 알림, 포트폴리오, 이번 주 결정·현재가, 가상 계좌, 핵심 뉴스).
시크릿: `EMAIL_SENDER`(발송 Gmail), `EMAIL_PASSWORD`(Gmail 앱 비밀번호), `INVEST_REPORT_TO`(쉼표 구분 수신자).
수동 발송: Actions → 투자 대시보드 업데이트 (Agent) → Run workflow → mode `report`.

## 주요 파일
- `run_weekly.py` prepare/finalize/interim, `aside_bridge.py` 결과 스키마 검증·비중 결정, `picks.py` 정량 점수·편입 규칙
- `sim.py` 가상 투자, `generate_invest.py` 대시보드 데이터, `index.html` 화면, `report_email.py` 메일
- `data/watchlist.json` 관심종목(매주 분석), `data/archive/` 주간 원자료 보존

## 나의 메모 (`memo/`)
메모장: https://juno99zz-arkt.github.io/Invest/memo/ — 비밀번호로 잠긴 개인 메모 Agent.
- **기본 포맷**: 제목 · 분류 · 항목(상태 칩: 준비→진행→완료→보류) · 자유 메모
- **주 단위 축적**: ISO 주(월~일)별로 쌓임, ‹ › 또는 목록으로 지난 주 열람
- **주간 정리**: 완료/진행/준비/보류별 묶음, 완료율, 공유용 요약 복사(한 줄 26자 이내)
- **자동 마감**: 새 주에 앱을 열면 지난 주를 마감하고 미완료(준비·진행) 항목을 다음 주 `이월 항목` 메모로 옮김 (설정에서 끔)
- **보안**: 브라우저에서 PBKDF2(60만 회)+AES-256-GCM 암호화 후 `memo/vault.json`(main)에 저장 — 저장소에는 암호문만 올라감. 비밀번호를 잊으면 복구 불가.
- **처음 설정**: GitHub → Settings → Developer settings → Fine-grained token → 이 저장소만, Contents: Read and write → 첫 화면의 토큰 칸에 입력 (토큰도 암호화되어 저장, 다른 기기에서는 비밀번호만 입력)
