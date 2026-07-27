import re


def get_cyclomatic_complexity(code_str: str) -> int:
    if not code_str:
        return 1

    text = code_str.lower()
    decision_points = 0
    for pattern in [r"\bif\b", r"\belif\b", r"\bfor\b", r"\bwhile\b", r"\bexcept\b", r"\bcase\b", r"&&", r"\|\|"]:
        decision_points += len(re.findall(pattern, text))

    score = max(1, 1 + decision_points)
    return score


def get_complexity_risk(score: int) -> str:
    if score <= 3:
        return "low"
    if score <= 7:
        return "medium"
    return "high"
