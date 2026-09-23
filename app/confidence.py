def calculate_confidence(plan, validation):

    if not validation["valid"]:
        return 0.0

    score = 0.40

    if plan.metric:
        score += 0.15

    if plan.operation:
        score += 0.15

    if plan.group_by:
        score += 0.10

    if plan.filters:
        score += 0.10

    if plan.sort:
        score += 0.05

    if plan.limit:
        score += 0.05

    return round(min(score, 1.0), 2)