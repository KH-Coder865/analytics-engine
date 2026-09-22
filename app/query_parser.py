import re


METRIC_ALIASES = {
    "sales": "revenue",
    "sale": "revenue",
    "revenue": "revenue",
    "income": "revenue",
    "earnings": "profit",
    "profit": "profit",
    "orders": "orders",
    "order": "orders",
    "aov": "avg_order_value",
    "average order value": "avg_order_value",
}


DIMENSIONS = [
    "region",
    "country",
    "city",
    "customer_segment",
    "product_category",
    "product_subcategory",
    "order_date",
]


def detect_metric(query):
    query_lower = query.lower()

    # Check longer phrases first
    for phrase in sorted(METRIC_ALIASES, key=len, reverse=True):
        if phrase in query_lower:
            return METRIC_ALIASES[phrase]

    return None


def detect_dimension(query):
    query_lower = query.lower()

    mappings = {
        "region": "region",
        "country": "country",
        "city": "city",
        "customer": "customer_id",
        "customer segment": "customer_segment",
        "category": "product_category",
        "product category": "product_category",
        "subcategory": "product_subcategory",
        "product": "product_name",
    }

    for phrase in sorted(mappings, key=len, reverse=True):
        if phrase in query_lower:
            return mappings[phrase]

    return None


def detect_limit(query):
    match = re.search(r"\btop\s+(\d+)", query.lower())

    if match:
        return int(match.group(1))

    return None


def detect_country(query):
    countries = [
        "India",
        "Germany",
        "USA",
        "UK",
        "France",
    ]

    query_lower = query.lower()

    for country in countries:
        if country.lower() in query_lower:
            return country

    return None


def detect_month(query):
    month_mapping = {
        "january": "01",
        "february": "02",
        "march": "03",
        "april": "04",
        "may": "05",
        "june": "06",
        "july": "07",
        "august": "08",
        "september": "09",
        "october": "10",
        "november": "11",
        "december": "12",
    }

    query_lower = query.lower()

    for month_name, month_number in month_mapping.items():
        if month_name in query_lower:
            return f"2024-{month_number}"

    return None


def parse_query(query):
    query_lower = query.lower()

    plan = {
        "metric": detect_metric(query),
        "dimension": detect_dimension(query),
        "limit": detect_limit(query),
        "country": detect_country(query),
        "month": detect_month(query),
        "sort": None,
        "operation": None,
    }

    if "top" in query_lower:
        plan["sort"] = "desc"

    if "average" in query_lower or "avg" in query_lower:
        plan["operation"] = "average"

    elif "total" in query_lower or "sum" in query_lower:
        plan["operation"] = "sum"

    elif "contribution" in query_lower:
        plan["operation"] = "contribution"

    elif "missed" in query_lower or "target" in query_lower:
        plan["operation"] = "target_comparison"

    elif "growth" in query_lower or "yoy" in query_lower:
        plan["operation"] = "yoy"

    return plan