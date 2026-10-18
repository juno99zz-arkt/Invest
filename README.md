# Invest — AI 투자 브리핑 대시보드 (Claude API 비용 0원)

대시보드: https://juno99zz-arkt.github.io/Invest/

정량 데이터 수집·결정·배포·메일은 GitHub Actions(무료)가, 웹검색 기반 시장 브리핑과 종목 심층분석은 **Agent**가 수행합니다.
Claude API(ANTHROPIC_API_KEY)는 더 이상 쓰지 않습니다.

## 주간 흐름

| 시각 (KST) | 주체 | 내용 |
|---|---|---|
| 토 06:00 | Actions `prepare` | 유니버스 정량 점수·신호 → 후보 선정 → `data/pending/request.json` (분석 요청서) |
| 토 07:00 | Agent | 요청서를 읽고 시장 브리핑(스탠스·뉴스·일정) + 종목 심층분석(판단표·데이터 검증) → `data/aside/result.json` 업로드 |
| 업로드 직후 | Actions `finalize` | 결과 검증 → 편입·유지·제외 결정 → 비중 → 이력·리포트 → 대시보드 배포 → **주간 메일 발송** |
| 토 21:00 | Actions `report` 안전망 | 그 주 메일이 아직 안 나갔으면 현재 대시보드 기준으로 발송 |
| 평일 07:00 | Agent | 보유 종목 뉴스·알림 점검 → 필요 시 중간 재평가 (`mode: interim`) |
| 매일 06:00 | Actions `daily` | 미국 장 마감 후 시세·PEG·상위 50 갱신, 변경 알림, 매도 신호 푸시 |
| 미국 장중 30분마다 | Actions `watch` | 보유 종목 가격 경고(약세 시나리오 도달·급락) 푸시 |

## 매도 신호 푸시 (`notify.py`, ntfy.sh)
- [매도] Agent 판단으로 보유 종목 제외 또는 비중 축소 → 즉시 푸시 (finalize 직후)
- [매도 경고] 약세 시나리오 가격 도달 / 분석 후 −10% / 편입가 −15% → 푸시, 다음 아침 Agent 재평가
- 시크릿 `NTFY_TOPIC`, 휴대폰 ntfy 앱에서 같은 토픽 구독. 같은 신호는 한 번만 (`data/push_log.json`). 테스트: mode `push_test`

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
