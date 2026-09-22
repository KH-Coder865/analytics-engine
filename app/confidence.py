def calculate_confidence(plan):

    score = 0.0

    if plan.get("metric"):
        score += 0.25

    if plan.get("operation"):
        score += 0.30

    if plan.get("dimension"):
        score += 0.20

    if plan.get("country") or plan.get("month"):
        score += 0.15

    if plan.get("limit") is not None:
        score += 0.10

    return round(min(score, 1.0), 2)