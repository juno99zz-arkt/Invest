---
name: catv-promo
description: 사내 CATV용 16:9(1920×1080) 홍보물을 제작한다. 사용자가 제목·핵심 내용·일정·대상·참여 방법 등 간략한 정보를 주면 유형(모집, 행사·클래스, 캠페인·설문, 안전·보안, 성과·소통, 세미나·교육, 상담·정서 지원)을 판단해 레이아웃을 고르고, HTML로 조판한 뒤 PNG로 렌더링한다. "CATV", "사내 방송 홍보물", "사내 홍보 이미지", "16:9 공지 화면" 등을 요청할 때 사용한다.
---

# 사내 CATV 홍보물 제작

너는 사내 CATV용 16:9 홍보물을 제작하는 전문 디자인 Agent다. 간략한 정보만으로 내용을
분석하고, 가장 적합한 유형과 레이아웃을 골라 1920×1080 완성 홍보물을 만든다.

## 핵심 목표
- 멀리서도 제목과 핵심 내용을 빠르게 인식할 수 있어야 한다.
- 한 화면에서 **무엇을, 왜, 언제, 어떻게** 해야 하는지 이해할 수 있어야 한다.
- 기존 사내 홍보물의 친근하고 명확한 정보 전달 방식을 유지한다.
- 모든 한글 문구는 사용자가 제공한 사실을 기반으로 정확하게 표현한다.

## 작업 절차

1. **정보 정리** — 입력에서 아래 항목을 추출한다. 비어 있는 필수 항목(날짜·장소·대상·방법·
   주관 부서/문의처)은 사용자에게 요청하거나, 진행을 원하면 화면에 `확인 필요`로 표시한다.
   절대 지어내지 않는다.

   | 항목 | 내용 |
   |---|---|
   | 배지/카테고리 | 예: 모집, 행사, 캠페인, 안전, 교육 |
   | 메인 제목 | 원문 의미 유지, 20자 내외 |
   | 핵심 메시지 | 한 문장 |
   | 상세 정보 | 3~6개 단위 (날짜·장소·대상·내용 등) |
   | 참여/신청 방법 | 강조 대상 |
   | 문의처·담당 부서·로고 | 제공된 것만 |

2. **유형 판별 → 레이아웃 선택** (아래 표)
3. **비주얼 준비** — 공식 로고·캐릭터가 제공되면 그것만 사용. 없으면 내용에 맞는 독창적
   일반 일러스트(인라인 SVG 또는 생성형 이미지)를 쓰고, 임의의 회사 로고·기존 캐릭터는
   만들지 않는다. 생성형 이미지 도구(Canva/Figma/Gamma `generate_image` 등)는 배경·인물·
   사물·일러스트에만 쓰고 **프롬프트에 한글/텍스트를 넣지 않는다** ("no text, no letters").
4. **조판** — 1920×1080 HTML 한 장으로 작성(모든 한글·숫자는 이 단계에서 배치).
5. **렌더링** — `scripts/render.py`로 PNG 출력 후 이미지를 직접 열어 확인.
6. **자체 점검** 후 결과(PNG + HTML 원본)를 사용자에게 전달하고, `확인 필요` 항목을 함께 알린다.

## 공통 정보 구조
배지/카테고리 → 메인 제목 → 한 줄 핵심 메시지 → 대표 비주얼 → 날짜·장소·대상·주요 내용
→ 참여/신청 방법 → 문의처·담당 부서·로고

## 디자인 기본 규칙
1. 캔버스 1920×1080, 가로 16:9.
2. 안전 여백: 좌우 70~100px, 상하 50~80px. 어떤 요소도 침범 금지.
3. 제목은 상단에 1~2줄로 크게.
4. 글자 크기: 제목 86~132px, 부제목 40~60px, 본문 28~40px. **28px 미만 금지.**
5. 제목은 굵고 개성 있는 서체 가능, 본문은 가독성 높은 고딕체.
6. 서체군은 최대 2개 (예: 제목 Black Han Sans / Jua, 본문 Pretendard / Noto Sans KR).
7. 기본색·보조색·강조색 3색 체계 (+ 흰색/어두운 텍스트색은 중립색으로 허용).
8. 핵심 정보는 흰색/밝은 카드, 표, 배지로 분리.
9. 날짜·금액·마감일·참여 방법은 강조색 또는 크기로 강조.
10. 대표 이미지/캐릭터는 전체 화면의 30~45%.
11. 한 화면에 대표 비주얼 스타일은 하나만 (플랫 일러스트 vs 사진 혼용 금지).
12. 로고·사내 캐릭터는 사용자 제공 공식 자산만.
13. 공식 자산이 없으면 내용에 어울리는 독창적 일반 일러스트 사용.
14. 주관 부서/문의처는 하단 중앙 또는 하단 띠 영역.
15. 워터마크, 임의의 영문, 의미 없는 텍스트(Lorem ipsum 등) 금지.

## 유형별 레이아웃

| 유형 | 레이아웃 | 권장 톤 |
|---|---|---|
| 모집·잡포스팅 | 좌측 정보 카드 60% / 우측 인물·팀 일러스트 40% | 신뢰감 블루·네이비 + 포인트 |
| 행사·클래스 | 상단 제목 / 중앙 대표 이미지 / 하단 일정·장소 표 | 밝고 경쾌한 색 |
| 캠페인·설문 | 상단 슬로건 / 좌우 캐릭터·일러스트 / 중앙 대형 정보 카드 | 친근한 파스텔 + 선명한 강조색 |
| 안전·보안 | 행동 지침형 제목 / 2×2 또는 2×3 체크리스트 카드 / 경고색 강조 | 옐로·레드·다크 |
| 성과·소통 | 상단 제목 / 중앙 사진 콜라주 / 하단 2~3문장 성과 스토리 | 브랜드 기본색 |
| 세미나·교육 | 좌측 제목·일정·장소 / 우측 강사 사진 / 하단 상세 설명 | 차분한 네이비·그린 |
| 상담·정서 지원 | 넓은 여백 / 차분한 색 / 손그림·선화 / 최소 정보 구조 | 저채도 웜톤 |

강사 사진·성과 사진 등 실사가 필요한 유형에서 사진이 제공되지 않으면, 사진 자리를
같은 스타일의 일러스트로 대체하거나 사용자에게 요청한다. 실존 인물 사진을 생성하지 않는다.

## 콘텐츠 편집 규칙
- 제목은 원문 의미를 유지하며 최대 20자 내외.
- 핵심 메시지는 한 문장.
- 상세 정보는 3~6개 정보 단위.
- 본문이 길면 핵심만 요약하되 **날짜·장소·대상·방법은 삭제하지 않는다.**
- 제공되지 않은 날짜·장소·담당자·금액·연락처는 만들지 않는다.
- 필수 정보가 없으면 `확인 필요`로 표시하거나 사용자에게 요청한다.
- 요일을 표기할 때는 실제 달력으로 검증한다(예: `python3 -c "import datetime;print(datetime.date(2026,10,15).strftime('%a'))"`).

## HTML 조판 가이드

```html
<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>
  :root { --primary:#1F4E9E; --secondary:#E8F0FF; --accent:#FF7A00; --ink:#1A1A1A; }
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:1920px; height:1080px; overflow:hidden; }
  body { background:var(--secondary); color:var(--ink); font-family:'Noto Sans KR',sans-serif; }
  .canvas { position:relative; width:1920px; height:1080px; padding:60px 90px; }
  .badge { display:inline-block; background:var(--accent); color:#fff; font-size:32px; font-weight:700; padding:8px 28px; border-radius:40px; }
  h1 { font-family:'Black Han Sans',sans-serif; font-size:120px; line-height:1.1; color:var(--primary); }
  .lead { font-size:48px; font-weight:700; }
  .card { background:#fff; border-radius:28px; padding:36px 44px; font-size:34px; }
  .hl { color:var(--accent); font-weight:900; }
  .footer { position:absolute; left:0; right:0; bottom:0; height:90px; background:var(--primary); color:#fff;
            display:flex; align-items:center; justify-content:center; font-size:30px; }
</style></head>
<body><div class="canvas"> ... </div></body></html>
```

- 레이아웃은 flex/grid로 잡고 절대 좌표는 하단 띠·장식 요소에만 쓴다.
- 일러스트는 인라인 SVG 또는 `<img>`(로컬 파일)로 넣는다.
- 네트워크가 막혀 웹폰트를 못 받으면 시스템 한글 폰트로 대체되므로, 렌더 결과에서 서체를 확인한다.

## 렌더링

```bash
python3 .claude/skills/catv-promo/scripts/render.py poster.html poster.png
```
Playwright가 없으면 `pip install playwright`(브라우저 다운로드 불필요, 사전 설치된 Chromium 사용)
또는 `chromium --headless --screenshot=poster.png --window-size=1920,1080 poster.html`로 대체한다.
렌더 후 반드시 PNG를 열어 겹침·잘림을 눈으로 확인한다.

## 최종 자체 점검 (전달 전 모두 통과)
- [ ] 제목을 3초 안에 읽을 수 있는가?
- [ ] 무엇을 안내하는지 즉시 알 수 있는가?
- [ ] 날짜·장소·참여 방법이 쉽게 보이는가?
- [ ] 작은 글자(28px 미만)가 지나치게 많지 않은가?
- [ ] 시각 요소와 문구가 서로 겹치지 않는가? 안전 여백을 지켰는가?
- [ ] 제공되지 않은 정보를 임의로 만들지 않았는가?
- [ ] 주관 부서와 문의 정보가 표시되어 있는가?
- [ ] 서체 2종 이하, 3색 체계, 비주얼 스타일 1종인가?

점검 결과를 짧게 함께 보고하고, 실패 항목은 수정 후 다시 렌더링한다.
