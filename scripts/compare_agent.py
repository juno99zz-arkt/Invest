"""클라우드 시험과 같은 날짜의 기존 분석을 비교한다. 거래·파일 갱신은 하지 않는다."""
import json
import sys
from pathlib import Path

baseline, trial = [json.loads(Path(p).read_text(encoding="utf-8")) for p in sys.argv[1:3]]
if baseline.get("week") != trial.get("week"):
    print("비교 보류: 기준일이 다름")
    sys.exit(1)
print("## 같은 날짜 분석 비교: " + str(trial.get("week")))
old, new = baseline.get("analyses", {}), trial.get("analyses", {})
print("| 종목 | 비교 |")
print("| --- | --- |")
differences = 0
for ticker in sorted(set(old) | set(new)):
    if ticker not in old or ticker not in new:
        print(f"| {ticker} | 분석 대상 차이 |")
        differences += 1
        continue
    changes = [k for k in ("verdict", "alert_level", "thesis_status", "conviction")
               if old[ticker].get(k) != new[ticker].get(k)]
    changes += ["decision_table." + k for k in ("action", "buy_below")
                if old[ticker].get("decision_table", {}).get(k) != new[ticker].get("decision_table", {}).get(k)]
    differences += bool(changes)
    print(f"| {ticker} | " + ("변경: " + ", ".join(changes) if changes else "주요 판정 동일") + " |")
weights_equal = baseline.get("target_weights") == trial.get("target_weights")
print("\n제안 비중: " + ("동일" if weights_equal else "차이 있음 — 근거 검토 필요"))
print(f"차이 종목 {differences}개. 자동 운영 전환은 수행하지 않음.")
