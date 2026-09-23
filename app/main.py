from .data_loader import (
    load_sales_data,
    load_targets,
    load_data_dictionary,
)

from .llm_parser import LLMQueryParser
from .query_executor import QueryExecutor
from .validator import validate_plan
from .confidence import calculate_confidence


def run_query(query):

    # -------------------------
    # Load data
    # -------------------------

    sales_df = load_sales_data()
    targets_df = load_targets()
    data_dictionary = load_data_dictionary()

    # -------------------------
    # Parse using LLM
    # -------------------------

    parser = LLMQueryParser(
        data_dictionary
    )

    plan = parser.parse(query)

    # -------------------------
    # Validate
    # -------------------------

    validation = validate_plan(plan)

    if not validation["valid"]:

        return {
            "query": query,
            "plan": plan.model_dump(),
            "result": None,
            "confidence_score": 0.0,
            "errors": validation["errors"],
        }

    # -------------------------
    # Confidence
    # -------------------------

    confidence = calculate_confidence(
        plan,
        validation
    )

    # -------------------------
    # Execute
    # -------------------------

    executor = QueryExecutor(
        sales_df,
        targets_df
    )

    result = executor.execute(plan)

    return {
        "query": query,
        "plan": plan.model_dump(),
        "result": result,
        "confidence_score": confidence,
    }


if __name__ == "__main__":

    query = input(
        "Enter your analytics query: "
    )

    response = run_query(query)

    print("\n" + "=" * 60)
    print("QUERY")
    print("=" * 60)

    print(response["query"])

    print("\n" + "=" * 60)
    print("PLAN")
    print("=" * 60)

    print(response["plan"])

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)

    print(response["result"])

    print("\n" + "=" * 60)
    print("CONFIDENCE")
    print("=" * 60)

    print(response["confidence_score"])