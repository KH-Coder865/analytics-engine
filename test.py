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


def main():

    queries = load_nl_queries()

    for item in queries:

        query = item["query"]

        try:
            response = run_query(query)

            result = make_json_serializable(
                response["result"]
            )

        except Exception as e:

            result = {
                "error": str(e)
            }

        output = {
            "query": query,
            "result": result,
        }

        print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
