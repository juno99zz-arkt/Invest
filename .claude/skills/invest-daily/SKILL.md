---
name: invest-daily
description: Invest 투자 대시보드의 매일 AI 분석(시장 브리핑 + 후보·보유 종목 심층분석 + 비중 제안)을 GitHub Actions 안에서 Claude Code가 수행하는 절차. 결과는 result.json 파일로만 쓰고, 반영(finalize)·커밋·메일·푸시는 워크플로가 한다.
---

# Invest 매일 AI 분석 (GitHub Actions · Claude Code)

Aside 루틴 "Invest 매일 AI 분석"(2026-11-07 기준)을 클라우드로 옮긴 판. 판단 규칙은 같고, 브라우저·업로드·메일·옵시디언 단계만 워크플로로 넘겼다.

## 하지 않는 일 (워크플로 담당)
- git 커밋·push, GitHub API 호출, Actions 실행, 메일·푸시 발송, 옵시디언 노트 저장
- `data/` 아래 기존 파일 수정 (출력 폴더 `$OUT` 만 쓴다)

## 입력 (워크플로가 미리 준비)
| 파일 | 내용 |
|---|---|
| `data/pending/request.json` | 오늘 요청서 (week = 오늘 KST 날짜). to_analyze · held · reused · dossiers · market_context · news_candidates · snaps · next_earnings |
| `work/context.json` | 대시보드 계산값: `alerts`(보유·관심 종목 경고), `fear_tier`(공포·탐욕 단계), `fear_candidates`, `holdings`(현재 비중), `today` |
| `work/dossiers/<TK>.json` | 종목별 dossier (req.dossiers 를 한 파일씩 나눈 것) |
| `data/analysis_cache.json` | 종목별 최근 분석 캐시 (재사용·재심사 판단용, 읽기만) |
| `data/risk_profile.json` | 비중 규칙 값 (읽기만) |
| `references/` | analysis_prompt.md(v2) · example_analysis.json · market_prompt.md(v2) · example_market_brief.json |

## 출력 (`$OUT` 폴더, 프롬프트가 경로를 알려줌)
- `$OUT/result.json` — finalize 가 읽는 결과 (아래 형식)
- `$OUT/analyses/<TK>.json` — 종목별 분석 원본
- `$OUT/note.json` — 옵시디언 노트용 `{ "summary": "2~3문장", "memo": ["오늘 확인한 것", ...3~6줄], "analyzed": ["TK", ...], "issues": ["..."] }`

## 1. 요청서 확인
- `request.week` 가 오늘(`context.today`)이 아니면 분석하지 말고 note.json 의 issues 에 "요청서가 오늘 날짜 아님(week=...)"만 쓰고 끝낸다.
- `request.finalized_at` 이 이미 오늘이면 같은 방식으로 "이미 반영됨"만 쓰고 끝낸다. **단, 프롬프트가 "시험 실행"이면 이 확인은 건너뛰고 끝까지 분석한다** (Aside 결과와 비교용).

## 2. 분석 대상 고르기 — 매일이므로 바뀐 것만
1. **req.to_analyze**: 새 후보, 캐시 재사용 조건이 깨진 종목(28일 경과·실적 발표·주가 ±15%·EPS 추정 ±5%·매수 기준가 도달). 모두 심층분석.
2. **매수 기준가 도달 재심사** (2026-11-07 규칙)
   - 현재가 ≤ buy_below 최초 도달(등호 포함), 위로 회복했다가 재진입, 재심사 미완료 → 새 분석 대상. 기존 캐시도 기준가 이하이면 최초 1회 재심사.
   - picks.py 의 buy_price_review_reason · observe_review_price 와 cache.price_review 가 상태를 관리한다. 실제 새 분석이 저장돼야 완료.
   - 새 분석 후에도 계속 기준가 이하인 것만으로 매일 반복 심층분석하지 않는다.
   - 요청서가 구버전이면 `data/analysis_cache.json` 과 `req.snaps` 로 직접 확인해, 재심사 대상은 req.reused 에 있어도 dossier 로 분석해 result.analyses 에 넣는다.
   - 재심사는 최신 공시·실적·추정치·정책/신용 위험을 확인하고, **가격 때문에 보류**인지 **비가격 위험 때문에 중단**인지 구분한다. 보유 경고 유지/해제, verdict·action, buy_below·시나리오·next_checks·change_triggers 를 현재가에 맞춰 일관되게 새로 쓴다. 가이던스 확인과 가격 조건이 AND 인지 OR 인지 명확히 한다.
   - 기준가 도달만으로 자동 매수하거나 과거 action/alert 만 바꿔 경고를 해제하지 않는다. 보류를 유지하면 구체적 이유와 재검토 조건을 note 에 쓴다. 섹터당 2종목 한도 등으로 편입이 막히면 실제 차단 사유를 쓴다.
3. **보유 종목(req.held)**: 최근 24~72시간 공시(8-K·실적·가이던스)·주요 뉴스를 WebSearch 로 확인한다. thesis_breakers·change_triggers 에 해당하거나, `context.alerts` 에 level "high"(실적 후 미재평가, ±10% 급변, 약세 가격 도달)가 있으면 to_analyze 에 없어도 재분석한다.
4. **공포·탐욕**: `context.fear_tier.tier ≥ 2`(지수 10·5 미만)이면 `fear_candidates` 중 eligible 이거나 매수 기준가 10% 이내 종목도 최신 자료로 재분석한다 (buy_below 를 억지로 올리지 않는다). 20 미만(watch)은 경계만.
5. 캐시에 decision_table 이 없는 구버전 분석은 재사용하지 말고 재분석한다.
6. 분석할 종목이 없어도 result.json 은 반드시 쓴다 (analyses 빈 객체). finalize 가 캐시와 오늘 가격으로 다시 판단해야 하기 때문.

## 3. 시장 브리핑 (메인 에이전트)
- **토요일**: `references/market_prompt.md` 전체 절차(뉴스 10건), `example_market_brief.json` 품질 기준.
- **평일**: 스탠스가 바뀔 만한 사건이 있을 때만 새로 쓴다(뉴스 5건 이상). 아니면 result 에서 `market_brief` 를 **빼면** finalize 가 직전 브리핑을 유지한다.
- 입력: req.market_context, req.news_candidates. WebSearch 는 핵심 사실·다음 14일 일정 확인용 5~8회.

## 4. 종목 심층분석 (서브에이전트 병렬)
- 종목마다 Task 서브에이전트 1개, 최대 8개 동시. 서브에이전트 프롬프트:
  1. "`.claude/skills/invest-daily/references/analysis_prompt.md` 와 `example_analysis.json` 을 읽고 그 지침·품질 기준을 따른다."
  2. 보유 종목이면 `보유 중인 종목 {TK}의 투자 논리를 재점검하세요.`, 아니면 `신규 편입 후보 {TK}를 분석하세요.` + `기준일: {req.date}` + 재분석 사유(fresh_reason·재심사·경고)
  3. "자료: `work/dossiers/{TK}.json` 을 읽는다."
  4. "공식 실적 발표·공시로 핵심 수치(data_conflicts 포함)를 먼저 검증하고, 최근 3~6개월 실적·가이던스·뉴스를 확인한 뒤, 결과 JSON 객체 하나를 `$OUT/analyses/{TK}.json` 에 Write 하라. 파일 외 다른 파일은 쓰지 마라."
- 모든 분석은 v2 스키마(data_checks · verified_metrics · evidence · decision_table · alert_level)를 채운다.
- 서브에이전트를 쓸 수 없으면 메인 에이전트가 같은 지침으로 순차 분석한다.

## 5. 비중 제안 (종목 선택과 분리)
계좌는 **최대 5종목 개별주 + 원화 현금** (ETF 없음). 실제 비중은 finalize 의 aside_bridge.size_portfolio 가 정하고, 여기서는 제안만 한다.
- `target_weights` {"NVDA": 20, ...}: 보유 종목은 변화가 없으면 지난 비중(`context.holdings`). 신규는 확신도별 기본 5→30 · 4→20 · 3→10 (낮출 수만 있음).
- `weights_reason`: 종목별 기대수익(약세25·기준50·강세25 가중)·약세 하락률·경고 단계 근거.
- 선택 `allocation` = {"equity_pct": N, "reason": "..."} — 스탠스별 상한(공격적 100 · 선별적 90 · 중립 80 · 방어적 60%)에서 ±10%p.
- 손실·종목·테마·섹터·전체 상한, 데이터 검증, 공포 규칙은 바꾸지 않는다. 좋은 후보가 없으면 현금이 정답. **주가 하락만으로 팔지 않는다.**

판정 규칙(참고, finalize 의 picks.decide 가 기계적으로 적용): 신규 편입 = '편입 적합' + 확신도 ≥ 4 + '검증 완료' (섹터당 2, 전체 5) · 탐색 편입 = 확신도 3 + '신규 매수' + 현재가 ≤ buy_below + 기대수익 ≥ 10% → 10% · 제외 = 붕괴·'논리 붕괴'·'부적합' · 교체 = 만석일 때 확신도 5 후보가 '약화'·확신도 ≤ 3 보유를 대체. 기준 충족 종목이 없으면 억지로 채우지 않는다.

## 6. result.json 조립 + 검증
```json
{ "week": "<req.week>", "analyzed_at": "<KST YYYY-MM-DD HH:MM>",
  "market_brief": { ... },            // 새로 쓴 날만
  "analyses": { "TK": { ... } },      // $OUT/analyses/*.json 을 모은 것
  "target_weights": { "TK": 20 }, "weights_reason": "...", "allocation": { ... } }
```
검증: `python aside_bridge.py data/pending/request.json $OUT/result.json`
- ✗ 항목이 있으면 해당 종목을 고치거나 재분석해 다시 검증한다. 2회 실패한 종목은 analyses 에서 빼고 note.issues 에 적는다 (finalize 가 '분석 실패로 판단 보류' 처리).

## 7. note.json
- summary: 오늘 무엇이 바뀌었고 왜, 매수·매도·비중 변화 제안, 다음에 볼 것 (2~3문장)
- memo: 재분석 이유·핵심 근거·공시/뉴스·공포·탐욕 단계 (3~6줄)
- 실제 보유자산·계좌·개인정보는 쓰지 않는다 (가상 계좌·공개 정보만).

## 마무리 출력
마지막 답변은 5줄 이내: 분석 종목, 판정 변화, 비중 제안 변화, 스탠스, 검증 결과(✓/✗ 수).
