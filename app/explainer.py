def explain_query(query, plan, confidence):

    parts = []

    if plan.get("metric"):
        parts.append(
            f"Metric: {plan['metric']}"
        )

    if plan.get("operation"):
        parts.append(
            f"Operation: {plan['operation']}"
        )

    if plan.get("dimension"):
        parts.append(
            f"Grouped by: {plan['dimension']}"
        )

    if plan.get("country"):
        parts.append(
            f"Country filter: {plan['country']}"
        )

    if plan.get("month"):
        parts.append(
            f"Month filter: {plan['month']}"
        )

    if plan.get("limit"):
        parts.append(
            f"Top: {plan['limit']}"
        )

    return {
        "query": query,
        "interpretation": " | ".join(parts),
        "confidence": confidence,
    }