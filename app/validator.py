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
    "month",
    "year",
    "quarter",
}


def validate_plan(plan):

    errors = []

    if plan.metric not in ALLOWED_METRICS:
        errors.append(
            f"Unsupported metric: {plan.metric}"
        )

    for dimension in plan.group_by:

        if dimension not in ALLOWED_DIMENSIONS:
            errors.append(
                f"Unsupported dimension: {dimension}"
            )

    for filter_item in plan.filters:

        if filter_item.column not in ALLOWED_DIMENSIONS:
            errors.append(
                f"Unsupported filter column: "
                f"{filter_item.column}"
            )

    if plan.limit is not None:

        if plan.limit <= 0:
            errors.append(
                "Limit must be greater than zero."
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }