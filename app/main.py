from .data_loader import (
    load_sales_data,
    load_targets,
)

from .query_parser import parse_query
from .query_engine import QueryEngine
from .validator import validate_plan
from .confidence import calculate_confidence
from .explainer import explain_query


def run_query(query):

    sales_df = load_sales_data()
    targets_df = load_targets()

    parser_output = parse_query(query)

    validation = validate_plan(parser_output)

    if not validation["valid"]:
        return {
            "query": query,
            "error": validation["errors"],
        }

    confidence = calculate_confidence(parser_output)

    engine = QueryEngine(
        sales_df,
        targets_df
    )

    result = engine.execute(parser_output)

    explanation = explain_query(
        query,
        parser_output,
        confidence
    )

    return {
        "query": query,
        "plan": parser_output,
        "result": result,
        "explanation": explanation,
    }


if __name__ == "__main__":

    queries = [
        "Total sales in India for March",
        "Top 2 cities by profit",
        "Average order value by region",
    ]

    for query in queries:

        print("\n" + "=" * 60)
        print(query)
        print("=" * 60)

        response = run_query(query)

        print(response)