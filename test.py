import json

from app.main import run_query
from app.data_loader import load_nl_queries


def make_json_serializable(value):
    """
    Convert pandas/numpy objects into JSON-serializable Python objects.
    """

    if hasattr(value, "to_dict"):
        try:
            return value.to_dict(orient="records")
        except TypeError:
            return value.to_dict()

    if isinstance(value, dict):
        return {
            key: make_json_serializable(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            make_json_serializable(item)
            for item in value
        ]

    return value


def generate_explanation(query, plan, result, confidence):
    """
    Generate a simple deterministic explanation from the query plan.
    """

    metric = plan.get("metric", "unknown")
    operation = plan.get("operation", "unknown")
    group_by = plan.get("group_by", [])
    filters = plan.get("filters", [])
    sort = plan.get("sort")
    limit = plan.get("limit")

    parts = []

    parts.append(
        f"Computed {operation} of {metric}"
    )

    if group_by:
        parts.append(
            f"grouped by {', '.join(group_by)}"
        )

    if filters:
        filter_text = ", ".join(
            f"{f['column']} {f['operator']} {f['value']}"
            for f in filters
        )
        parts.append(
            f"with filters: {filter_text}"
        )

    if sort:
        parts.append(
            f"sorted by {sort['column']} "
            f"in {sort['direction']}ending order"
        )

    if limit:
        parts.append(
            f"limited to {limit} result(s) per group"
            if len(group_by) > 1
            else f"limited to {limit} result(s)"
        )

    parts.append(
        f"confidence score is {confidence:.2f}"
    )

    return ", ".join(parts) + "."


def main():

    queries = load_nl_queries()

    for item in queries:

        query = item["query"]

        try:
            response = run_query(query)

            plan = response.get("plan", {})
            result = make_json_serializable(
                response.get("result")
            )
            confidence = response.get(
                "confidence_score",
                0.0
            )

            generated_logic = json.dumps(
                plan,
                ensure_ascii=False
            )

            explanation = generate_explanation(
                query,
                plan,
                result,
                confidence
            )

        except Exception as e:

            generated_logic = ""
            result = {
                "error": str(e)
            }
            confidence = 0.0
            explanation = (
                "The query could not be executed: "
                + str(e)
            )

        output = {
            "query": query,
            "generated_logic": generated_logic,
            "result": result,
            "confidence_score": confidence,
            "explanation": explanation,
        }

        print(
            json.dumps(
                output,
                indent=2,
                ensure_ascii=False,
                default=str
            )
        )


if __name__ == "__main__":
    main()
