ALLOWED_METRICS = {
    "revenue",
    "profit",
    "orders",
    "avg_order_value",
}

ALLOWED_DIMENSIONS = {
    "region",
    "country",
    "city",
    "customer_id",
    "customer_segment",
    "product_category",
    "product_subcategory",
    "product_name",
    "order_date",
}


def validate_plan(plan):

    errors = []

    metric = plan.get("metric")
    dimension = plan.get("dimension")

    if metric and metric not in ALLOWED_METRICS:
        errors.append(
            f"Unsupported metric: {metric}"
        )

    if dimension and dimension not in ALLOWED_DIMENSIONS:
        errors.append(
            f"Unsupported dimension: {dimension}"
        )

    limit = plan.get("limit")

    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            errors.append(
                "Limit must be a positive integer."
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }