import re


def get_cyclomatic_complexity(code_str: str) -> int:
    """
    Calculates Cyclomatic Complexity (M = 1 + decision_points).
    Decision points include: if, elif, for, while, except, case, &&, ||
    """
    if not code_str:
        return 1

    text = code_str.lower()
    decision_keywords = [
        r"\bif\b", r"\belif\b", r"\bfor\b", r"\bwhile\b",
        r"\bexcept\b", r"\bcase\b", r"&&", r"\|\|"
    ]

    decision_points = 0
    for pattern in decision_keywords:
        decision_points += len(re.findall(pattern, text))

    return max(1, 1 + decision_points)


def get_complexity_risk(score: int) -> str:
    """Categorize complexity score into risk level: low (1-3), medium (4-7), high (8+)."""
    if score <= 3:
        return "low"
    if score <= 7:
        return "medium"
    return "high"
