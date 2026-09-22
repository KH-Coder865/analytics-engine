from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Filter(BaseModel):
    column: str
    operator: Literal["=", "!=", ">", "<", ">=", "<=", "contains"]
    value: str


class Sort(BaseModel):
    column: str
    direction: Literal["asc", "desc"]


class QueryPlan(BaseModel):
    metric: str
    operation: Literal[
        "sum",
        "average",
        "count",
        "contribution",
        "target_comparison",
        "yoy"
    ]

    group_by: List[str] = Field(default_factory=list)

    filters: List[Filter] = Field(default_factory=list)

    sort: Optional[Sort] = None

    limit: Optional[int] = None