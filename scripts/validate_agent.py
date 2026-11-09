"""클라우드 분석 계약 검사. 평일 시장 브리핑 생략은 허용하고 다른 누락은 실패한다."""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aside_bridge import load_result, resolve_weights


def validate(request, result):
    _, analyses, errors = load_result(request, result)
    # 분석 스킬 3절: 평일에는 직전 시장 브리핑을 재사용한다.
    if date.fromisoformat(request["week"]).weekday() != 5 and "market_brief" not in result:
        errors = [e for e in errors if e != "market_brief 없음"]
    weights = result.get("target_weights")
    if not isinstance(weights, dict):
        errors.append("target_weights 없음 또는 객체 아님")
    elif any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in weights.values()):
        errors.append("비중은 숫자여야 함")
    else:
        _, notes = resolve_weights(weights, list(weights), {})
        errors.extend(notes)
    return analyses, errors


if __name__ == "__main__":
    request = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    result = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    analyses, errors = validate(request, result)
    print(f"종목 검증 {sum(a is not None for a in analyses.values())}/{len(analyses)}")
    for error in errors:
        print("검증 실패:", error)
    sys.exit(1 if errors else 0)
