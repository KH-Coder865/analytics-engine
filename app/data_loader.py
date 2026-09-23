import json
import pandas as pd

from .config import (
    SALES_DATA_PATH,
    TARGETS_DATA_PATH,
    DATA_DICTIONARY_PATH,
    NL_QUERIES_PATH,
)


def load_sales_data():
    df = pd.read_csv(SALES_DATA_PATH, keep_default_na=False)

    df["order_date"] = pd.to_datetime(df["order_date"])

    # Derived time dimensions
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    df["quarter"] = df["order_date"].dt.to_period("Q").astype(str)

    # Revenue defined by the data dictionary
    df["revenue"] = (
        df["quantity"]
        * df["unit_price"]
        * (1 - df["discount"])
    )

    return df


def load_targets():
    df = pd.read_csv(TARGETS_DATA_PATH)
    return df


def load_data_dictionary():
    with open(DATA_DICTIONARY_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_nl_queries():
    with open(NL_QUERIES_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)