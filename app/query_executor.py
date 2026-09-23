import pandas as pd

from .schemas import QueryPlan


class QueryExecutor:

    def __init__(self, sales_df, targets_df):

        self.sales_df = sales_df.copy()
        self.targets_df = targets_df.copy()

    def execute(self, plan: QueryPlan):

        df = self.sales_df.copy()

        # -------------------------
        # Apply filters
        # -------------------------

        for filter_item in plan.filters:

            column = filter_item.column
            operator = filter_item.operator
            value = filter_item.value

            if column not in df.columns:
                raise ValueError(
                    f"Unknown filter column: {column}"
                )

            if operator == "=":
                df = df[df[column].astype(str) == str(value)]

            elif operator == "!=":
                df = df[df[column].astype(str) != str(value)]

            elif operator == ">":
                df = df[df[column] > float(value)]

            elif operator == "<":
                df = df[df[column] < float(value)]

            elif operator == ">=":
                df = df[df[column] >= float(value)]

            elif operator == "<=":
                df = df[df[column] <= float(value)]

            elif operator == "contains":
                df = df[
                    df[column]
                    .astype(str)
                    .str.contains(
                        str(value),
                        case=False,
                        na=False
                    )
                ]

        # -------------------------
        # Target comparison
        # -------------------------

        if plan.operation == "target_comparison":
            return self._target_comparison(df, plan)

        # -------------------------
        # YoY
        # -------------------------

        if plan.operation == "yoy":
            return self._yoy(df, plan)

        # -------------------------
        # Contribution
        # -------------------------

        if plan.operation == "contribution":
            return self._contribution(df, plan)

        # -------------------------
        # Normal aggregation
        # -------------------------

        result = self._aggregate(df, plan)

        # -------------------------
        # Sorting
        # -------------------------

        if plan.sort:

            sort_column = plan.sort.column

            if sort_column in result.columns:

                result = result.sort_values(
                    sort_column,
                    ascending=(
                        plan.sort.direction == "asc"
                    )
                )

        # -------------------------
        # Limit
        # -------------------------

        if plan.limit:
            result = result.head(plan.limit)

        return result.to_dict(orient="records")

    def _aggregate(self, df, plan):

        metric = plan.metric
        operation = plan.operation
        group_by = plan.group_by

        # --------------------------------
        # Average Order Value
        # --------------------------------

        if metric == "avg_order_value":

            if group_by:

                result = (
                    df.groupby(group_by)
                    .agg(
                        revenue=("revenue", "sum"),
                        orders=("order_id", "count")
                    )
                    .reset_index()
                )

                result["avg_order_value"] = (
                    result["revenue"] / result["orders"]
                )

                return result[
                    group_by + ["avg_order_value"]
                ]

            revenue = df["revenue"].sum()
            orders = df["order_id"].count()

            value = revenue / orders if orders else 0

            return pd.DataFrame([
                {
                    "value": float(value)
                }
            ])

        # --------------------------------
        # Normal metrics
        # --------------------------------

        if metric == "revenue":
            value_column = "revenue"

        elif metric == "profit":
            value_column = "profit"

        elif metric == "orders":
            value_column = "order_id"

        else:
            raise ValueError(
                f"Unsupported metric: {metric}"
            )

        # --------------------------------
        # No grouping
        # --------------------------------

        if not group_by:

            if operation == "sum":
                value = df[value_column].sum()

            elif operation == "count":
                value = df[value_column].count()

            elif operation == "average":
                value = df[value_column].mean()

            else:
                raise ValueError(
                    f"Unsupported operation: {operation}"
                )

            return pd.DataFrame([
                {
                    "value": float(value)
                    if pd.notna(value)
                    else 0
                }
            ])

        # --------------------------------
        # Grouped sum
        # --------------------------------

        if operation == "sum":

            result = (
                df.groupby(group_by)[value_column]
                .sum()
                .reset_index()
            )

            result = result.rename(
                columns={
                    value_column: metric
                }
            )

            return result

        # --------------------------------
        # Grouped count
        # --------------------------------

        if operation == "count":

            result = (
                df.groupby(group_by)[value_column]
                .count()
                .reset_index()
            )

            result = result.rename(
                columns={
                    value_column: "orders"
                }
            )

            return result

        # --------------------------------
        # Grouped average
        # --------------------------------

        if operation == "average":

            result = (
                df.groupby(group_by)[value_column]
                .mean()
                .reset_index()
            )

            result = result.rename(
                columns={
                    value_column: metric
                }
            )

            return result

        raise ValueError(
            f"Unsupported operation: {operation}"
        )

        # # No GROUP BY
        # if not group_by:

        #     if operation == "sum":
        #         value = df[value_column].sum()

        #     elif operation == "count":
        #         value = df[value_column].count()

        #     elif operation == "average":
        #         value = df[value_column].mean()

        #     else:
        #         raise ValueError(
        #             f"Unsupported operation: {operation}"
        #         )

        #     return pd.DataFrame([
        #         {
        #             "value": float(value)
        #             if pd.notna(value)
        #             else 0
        #         }
        #     ])

        # # GROUP BY
        # if operation == "sum":

        #     result = (
        #         df.groupby(group_by)[value_column]
        #         .sum()
        #         .reset_index()
        #     )

        #     result = result.rename(
        #         columns={
        #             value_column: metric
        #         }
        #     )

        #     return result

        # if operation == "count":

        #     result = (
        #         df.groupby(group_by)[value_column]
        #         .count()
        #         .reset_index()
        #     )

        #     result = result.rename(
        #         columns={
        #             value_column: "orders"
        #         }
        #     )

        #     return result

        # if operation == "average":

        #     result = (
        #         df.groupby(group_by)[value_column]
        #         .mean()
        #         .reset_index()
        #     )

        #     result = result.rename(
        #         columns={
        #             value_column: metric
        #         }
        #     )

        #     return result

        # raise ValueError(
        #     f"Unsupported operation: {operation}"
        # )

    def _contribution(self, df, plan):

        if plan.metric != "revenue":
            raise ValueError(
                "Contribution currently supports revenue only."
            )

        if not plan.group_by:
            raise ValueError(
                "Contribution requires a group_by dimension."
            )

        grouped = (
            df.groupby(plan.group_by)["revenue"]
            .sum()
            .reset_index()
        )

        total = grouped["revenue"].sum()

        if total == 0:
            grouped["contribution_pct"] = 0.0
        else:
            grouped["contribution_pct"] = (
                grouped["revenue"] / total * 100
            )

        return grouped

    def _target_comparison(self, df, plan):

        revenue = (
            df.groupby("region")["revenue"]
            .sum()
            .reset_index()
        )

        if not plan.filters:
            raise ValueError(
                "Target comparison requires a month filter."
            )

        month = None

        for filter_item in plan.filters:
            if filter_item.column == "month":
                month = filter_item.value

        if month is None:
            raise ValueError(
                "Target comparison requires a month filter."
            )

        targets = self.targets_df[
            self.targets_df["month"] == month
        ]

        result = revenue.merge(
            targets,
            on="region",
            how="left"
        )

        result["missed_target"] = (
            result["revenue"] < result["target_revenue"]
        )

        return result

    def _yoy(self, df, plan):

        if plan.metric != "revenue":
            raise ValueError(
                "YoY currently supports revenue."
            )

        yearly = (
            df.groupby("year")["revenue"]
            .sum()
            .sort_index()
        )

        if len(yearly) < 2:
            return pd.DataFrame([
                {
                    "error": (
                        "At least two years "
                        "of data are required."
                    )
                }
            ])

        current_year = yearly.index[-1]
        previous_year = yearly.index[-2]

        current = yearly.iloc[-1]
        previous = yearly.iloc[-2]

        if previous == 0:
            growth = None
        else:
            growth = (
                (current - previous)
                / previous
                * 100
            )

        return pd.DataFrame([
            {
                "current_year": int(current_year),
                "previous_year": int(previous_year),
                "current_revenue": float(current),
                "previous_revenue": float(previous),
                "growth_pct": growth,
            }
        ])