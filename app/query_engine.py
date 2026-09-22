import pandas as pd


class QueryEngine:

    def __init__(self, sales_df, targets_df):
        self.sales_df = sales_df.copy()
        self.targets_df = targets_df.copy()

    def execute(self, plan):

        operation = plan.get("operation")
        metric = plan.get("metric")
        dimension = plan.get("dimension")

        df = self.sales_df.copy()

        # Apply country filter
        if plan.get("country"):
            df = df[df["country"] == plan["country"]]

        # Apply month filter
        if plan.get("month"):
            df = df[df["month"] == plan["month"]]

        if operation == "sum":
            return self._sum(df, metric, dimension)

        if operation == "average":
            return self._average(df, metric, dimension)

        if operation == "contribution":
            return self._contribution(df, metric, dimension)

        if operation == "target_comparison":
            return self._target_comparison(df, plan)

        if operation == "yoy":
            return self._yoy(df, metric)

        if plan.get("limit"):
            return self._top_n(df, metric, dimension, plan["limit"])

        return {
            "error": "Unable to determine the analytical operation."
        }

    def _sum(self, df, metric, dimension=None):

        if metric == "revenue":
            value_column = "revenue"
        else:
            value_column = metric

        if dimension:
            result = (
                df.groupby(dimension)[value_column]
                .sum()
                .sort_values(ascending=False)
            )

            limit = None

            return result.reset_index().to_dict(orient="records")

        return {
            "value": float(df[value_column].sum())
        }

    def _average(self, df, metric, dimension=None):

        if metric == "avg_order_value":
            if dimension:
                result = (
                    df.groupby(dimension)
                    .agg(
                        revenue=("revenue", "sum"),
                        orders=("order_id", "count"),
                    )
                )

                result["avg_order_value"] = (
                    result["revenue"] / result["orders"]
                )

                return (
                    result["avg_order_value"]
                    .reset_index()
                    .to_dict(orient="records")
                )

            orders = df["order_id"].count()

            if orders == 0:
                return {"value": 0}

            return {
                "value": float(df["revenue"].sum() / orders)
            }

        return {"error": "Unsupported average metric."}

    def _contribution(self, df, metric, dimension):

        if metric != "revenue":
            return {
                "error": "Contribution currently supports revenue."
            }

        grouped = (
            df.groupby(dimension)["revenue"]
            .sum()
            .reset_index()
        )

        total = grouped["revenue"].sum()

        if total == 0:
            grouped["contribution_pct"] = 0
        else:
            grouped["contribution_pct"] = (
                grouped["revenue"] / total * 100
            )

        return grouped.to_dict(orient="records")

    def _target_comparison(self, df, plan):

        if not plan.get("month"):
            return {
                "error": "A month is required for target comparison."
            }

        revenue = (
            df.groupby("region")["revenue"]
            .sum()
            .reset_index()
        )

        targets = self.targets_df[
            self.targets_df["month"] == plan["month"]
        ]

        result = revenue.merge(
            targets,
            on="region",
            how="left"
        )

        result["missed_target"] = (
            result["revenue"] < result["target_revenue"]
        )

        return result.to_dict(orient="records")

    def _yoy(self, df, metric):

        if metric != "revenue":
            return {
                "error": "YoY currently supports revenue."
            }

        yearly = (
            df.groupby("year")["revenue"]
            .sum()
            .sort_index()
        )

        if len(yearly) < 2:
            return {
                "error": "At least two years of data are required."
            }

        current = yearly.iloc[-1]
        previous = yearly.iloc[-2]

        if previous == 0:
            return {
                "error": "Previous year revenue is zero."
            }

        growth = (current - previous) / previous * 100

        return {
            "current_year": int(yearly.index[-1]),
            "previous_year": int(yearly.index[-2]),
            "current_revenue": float(current),
            "previous_revenue": float(previous),
            "growth_pct": float(growth),
        }

    def _top_n(self, df, metric, dimension, n):

        if not dimension:
            return {
                "error": "A dimension is required for top-N queries."
            }

        value_column = metric

        result = (
            df.groupby(dimension)[value_column]
            .sum()
            .sort_values(ascending=False)
            .head(n)
        )

        return result.reset_index().to_dict(orient="records")