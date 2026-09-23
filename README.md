# Intelligent Analytics Query Engine

An AI-assisted analytics query engine that converts natural-language
business questions into **structured, validated, and executable
analytical queries** over tabular sales data.

The project combines **GenAI/NLP interpretation** with a **controlled
pandas execution layer**. The language model is responsible for
understanding the user's intent and producing a structured query plan,
while validation and execution remain deterministic and constrained.

------------------------------------------------------------------------

## 1. Project Overview

Business users often want to ask questions such as:

-   "Total sales in India for March"
-   "Top 2 cities by profit"
-   "Average order value by region"
-   "Which region missed its target in Feb?"
-   "Sales contribution % by category"

Traditional analytics systems usually require the user to know SQL,
Python, or a predefined dashboard structure.

This project provides a natural-language interface:

``` text
Natural Language Query
        ↓
     LLM Parser
        ↓
 Structured Query Plan
        ↓
 Pydantic Validation
        ↓
 Confidence Estimation
        ↓
 Controlled Pandas Execution
        ↓
     Analytical Result
```

The key design principle is:

> **The LLM interprets the query; it does not execute arbitrary code.**

This keeps the system flexible enough to understand natural language
while keeping analytical execution deterministic and constrained.

------------------------------------------------------------------------

## 2. Features

### Natural-language analytics

Users can ask business questions using ordinary language rather than
writing SQL or Python.

### GenAI-powered query parsing

The system uses a Groq-hosted LLM to translate natural-language
questions into a structured `QueryPlan`.

### Structured query plans

Instead of allowing the LLM to generate arbitrary Python or SQL, the
model must return a constrained JSON structure containing fields such
as:

-   metric
-   operation
-   group-by dimensions
-   filters
-   sorting
-   result limit

### Schema validation

Pydantic validates the LLM-generated query plan before it reaches the
execution layer.

### Controlled execution

The executor uses predefined pandas operations rather than executing
generated code.

### Business metric definitions

The data dictionary provides canonical definitions and synonyms, for
example:

``` text
sales → revenue
income → revenue
earnings → profit
orders → count(order_id)
aov → avg_order_value
```

Revenue is defined as:

``` text
quantity × unit_price × (1 - discount)
```

### Confidence scoring

Each successfully validated query receives a confidence score between
`0` and `1`.

The current implementation uses deterministic signals from the generated
plan rather than allowing the LLM to freely invent a confidence value.

### Benchmark dataset

The repository contains a set of natural-language benchmark queries with
expected analytical logic.

### Extensible architecture

The query representation can be extended to support more advanced
analytical operations such as:

-   ranking
-   top-N per group
-   nested aggregations
-   window-style operations
-   additional time-series analysis

------------------------------------------------------------------------

## 3. Tech Stack

  Component                   Technology
  --------------------------- ----------------------
  Language                    Python
  Data processing             Pandas
  Numerical processing        NumPy
  LLM provider                Groq
  LLM model                   `openai/gpt-oss-20b`
  Schema validation           Pydantic
  Environment configuration   python-dotenv
  Testing                     pytest
  Query execution             Pandas
  Data format                 CSV / JSON

------------------------------------------------------------------------

## 4. Project Structure

``` text
analytics-engine/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── llm_parser.py
│   ├── schemas.py
│   ├── validator.py
│   ├── confidence.py
│   ├── query_executor.py
│   ├── main.py
│   │
│   ├── query_parser.py
│   ├── query_engine.py
│   └── explainer.py
│
├── dataset/
│   ├── sales_data.csv
│   ├── targets.csv
│   ├── data_dictionary.json
│   └── nl_queries.json
│
├── tests/
│
├── test.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

### Main modules

#### `app/config.py`

Contains project paths and environment configuration.

It defines the locations of:

-   sales data
-   target data
-   data dictionary
-   benchmark queries

------------------------------------------------------------------------

#### `app/data_loader.py`

Loads the datasets and performs initial preprocessing.

The sales dataset receives additional derived columns:

``` text
year
month
quarter
revenue
```

Revenue is calculated as:

``` python
df["revenue"] = (
    df["quantity"]
    * df["unit_price"]
    * (1 - df["discount"])
)
```

------------------------------------------------------------------------

#### `app/schemas.py`

Defines the structured query representation using Pydantic.

The current query plan contains:

``` text
metric
operation
group_by
filters
sort
limit
```

This schema acts as the contract between the LLM and the execution
engine.

------------------------------------------------------------------------

#### `app/llm_parser.py`

Responsible for converting natural-language questions into a
`QueryPlan`.

The parser:

1.  Loads the data dictionary.
2.  Provides metric and dimension definitions to the LLM.
3.  Provides explicit parsing rules.
4.  Requests JSON output.
5.  Parses the returned JSON.
6.  Validates it using the Pydantic schema.

The model is configured with:

``` text
openai/gpt-oss-20b
```

and deterministic temperature:

``` text
temperature = 0
```

------------------------------------------------------------------------

#### `app/validator.py`

Performs additional validation of the generated query plan.

It checks:

-   supported metrics
-   supported dimensions
-   supported filter columns
-   valid limits

This provides a second layer of protection after Pydantic validation.

------------------------------------------------------------------------

#### `app/confidence.py`

Calculates a deterministic confidence score.

The score considers whether the generated plan contains expected
components such as:

-   metric
-   operation
-   grouping
-   filters
-   sorting
-   limit

Invalid plans receive:

``` text
0.0
```

------------------------------------------------------------------------

#### `app/query_executor.py`

Executes validated query plans using pandas.

It currently supports operations including:

``` text
sum
average
count
contribution
target_comparison
yoy
```

Supported metrics include:

``` text
revenue
profit
orders
avg_order_value
```

The executor is deliberately separated from the LLM so that generated
natural-language interpretation cannot directly execute arbitrary
Python.

------------------------------------------------------------------------

#### `app/main.py`

Provides the main application flow.

The `run_query()` function performs:

``` text
Load data
    ↓
Load dictionary
    ↓
Parse natural language
    ↓
Validate plan
    ↓
Calculate confidence
    ↓
Execute query
    ↓
Return structured response
```

------------------------------------------------------------------------

#### `test.py`

Runs the benchmark queries from:

``` text
dataset/nl_queries.json
```

and prints the query together with its result.

This provides a simple end-to-end evaluation of the query engine.

------------------------------------------------------------------------

## 5. Dataset

The project uses four dataset/configuration files.

### `sales_data.csv`

Contains the transactional sales data.

Important fields include:

``` text
order_id
order_date
region
country
city
customer_id
customer_segment
product_category
product_subcategory
product_name
quantity
unit_price
discount
shipping_cost
profit
```

The engine derives:

``` text
year
month
quarter
revenue
```

from the raw data.

------------------------------------------------------------------------

### `targets.csv`

Contains regional monthly revenue targets.

Example:

``` text
region,month,target_revenue
APAC,2024-01,5000
APAC,2024-02,6000
APAC,2024-03,7000
```

This enables target-comparison queries.

------------------------------------------------------------------------

### `data_dictionary.json`

Defines the semantic vocabulary of the analytics engine.

Example:

``` json
{
  "metrics": {
    "revenue": "quantity * unit_price * (1 - discount)",
    "profit": "profit",
    "orders": "count(order_id)",
    "avg_order_value": "revenue / orders"
  }
}
```

It also contains:

-   supported dimensions
-   synonyms
-   time mappings

The dictionary is passed to the LLM so that the model works against the
same semantic definitions used by the executor.

------------------------------------------------------------------------

### `nl_queries.json`

Contains the natural-language benchmark questions and their expected
analytical logic.

The current benchmark includes eight queries covering:

1.  Filtered aggregation
2.  Top-N ranking
3.  Grouped average order value
4.  Target comparison
5.  Contribution percentage
6.  Per-group top product
7.  Year-over-year growth
8.  Nested top-customer analysis

------------------------------------------------------------------------

## 6. Query Processing Pipeline

A query travels through several layers.

### Step 1 --- Natural-language input

Example:

``` text
Total sales in India for March
```

------------------------------------------------------------------------

### Step 2 --- LLM interpretation

The LLM converts the question into a structured plan.

Conceptually:

``` json
{
  "metric": "revenue",
  "operation": "sum",
  "group_by": [],
  "filters": [
    {
      "column": "country",
      "operator": "=",
      "value": "India"
    },
    {
      "column": "month",
      "operator": "=",
      "value": "2024-03"
    }
  ],
  "sort": null,
  "limit": null
}
```

------------------------------------------------------------------------

### Step 3 --- Schema validation

Pydantic checks that the generated JSON follows the expected structure.

For example, operators are restricted to:

``` text
=
!=
>
<
>=
<=
contains
```

This prevents unsupported structures from reaching the executor.

------------------------------------------------------------------------

### Step 4 --- Semantic validation

The validator checks that:

-   the metric exists
-   dimensions are supported
-   filter columns are supported
-   limits are valid

------------------------------------------------------------------------

### Step 5 --- Confidence calculation

A deterministic confidence score is generated from the validated plan.

------------------------------------------------------------------------

### Step 6 --- Controlled execution

The query executor maps the plan to known pandas operations.

For example:

``` text
metric = revenue
operation = sum
filter = country == India
filter = month == 2024-03
```

becomes a controlled pandas aggregation rather than generated Python
code.

------------------------------------------------------------------------

### Step 7 --- Result

The result is returned as a pandas DataFrame internally and converted to
JSON-compatible output by the benchmark runner.

------------------------------------------------------------------------

## 7. Supported Query Types

### 7.1 Simple aggregation

Example:

``` text
Total sales in India for March
```

Equivalent analytical logic:

``` text
SUM(revenue)
WHERE country = 'India'
AND month = '2024-03'
```

------------------------------------------------------------------------

### 7.2 Grouped aggregation

Example:

``` text
Top 2 cities by profit
```

Conceptually:

``` text
GROUP BY city
ORDER BY SUM(profit) DESC
LIMIT 2
```

------------------------------------------------------------------------

### 7.3 Average order value

Example:

``` text
Average order value by region
```

The engine calculates:

``` text
SUM(revenue) / COUNT(order_id)
```

for each region.

------------------------------------------------------------------------

### 7.4 Target comparison

Example:

``` text
Which region missed its target in Feb?
```

The engine:

1.  Aggregates regional revenue.
2.  Identifies the requested month.
3.  Loads the corresponding target values.
4.  Joins revenue with targets.
5.  Compares actual revenue with target revenue.

------------------------------------------------------------------------

### 7.5 Contribution percentage

Example:

``` text
Sales contribution % by category
```

Conceptually:

``` text
category revenue
---------------- × 100
total revenue
```

------------------------------------------------------------------------

### 7.6 Year-over-year analysis

Example:

``` text
YoY growth in revenue
```

The engine compares revenue across years.

If the dataset does not contain both the current and previous year, the
engine returns an explicit error instead of fabricating a value.

For example:

``` json
[
  {
    "error": "At least two years of data are required."
  }
]
```

This is intentional: analytical systems should report insufficient data
rather than invent missing historical values.

------------------------------------------------------------------------

## 8. Advanced Query Handling

Some natural-language questions require more than a single aggregation.

For example:

``` text
Top product in each region
```

requires:

``` text
GROUP BY region + product
        ↓
Calculate revenue
        ↓
Rank products within each region
        ↓
Keep the top product
```

Similarly:

``` text
Revenue of top 3 customers per region
```

requires:

``` text
GROUP BY region + customer
        ↓
Calculate customer revenue
        ↓
Rank customers within each region
        ↓
Keep top 3
        ↓
Aggregate their revenue by region
```

These operations are represented as higher-level analytical plans rather
than arbitrary generated code.

The query-plan schema is designed to be extended with ranking/window
semantics for these nested operations.

------------------------------------------------------------------------

## 9. Why Use an LLM?

A traditional rule-based parser could handle a fixed set of phrases, but
natural-language business questions have many variations.

For example, all of these can refer to revenue:

``` text
sales
income
revenue
earnings
```

And a user may phrase the same intent as:

``` text
Show sales for India in March
```

or:

``` text
What was the revenue generated in India during March?
```

The LLM provides the language understanding layer.

However, it is **not trusted with execution**.

The architecture deliberately separates:

``` text
Language understanding
        ≠
Analytical execution
```

This makes the system easier to validate, test, and extend.

------------------------------------------------------------------------

## 10. Why Structured Query Plans?

An alternative approach would be:

``` text
User query
    ↓
LLM
    ↓
Generated Python / SQL
    ↓
Execute
```

That approach has significant drawbacks.

The model could generate:

-   invalid syntax
-   unsupported columns
-   incorrect calculations
-   unintended operations
-   arbitrary code

This project instead uses:

``` text
User query
    ↓
LLM
    ↓
Structured JSON
    ↓
Pydantic validation
    ↓
Controlled executor
```

The model can only express operations that the application explicitly
supports.

------------------------------------------------------------------------

## 11. Confidence Scoring

The confidence score currently uses deterministic features of the query
plan.

The base score is:

``` text
0.40
```

Additional points are assigned when relevant plan components are
present:

  Component      Contribution
  ------------ --------------
  Valid plan         Required
  Metric                +0.15
  Operation             +0.15
  Grouping              +0.10
  Filters               +0.10
  Sorting               +0.05
  Limit                 +0.05

The final score is capped at:

``` text
1.0
```

This is intentionally a simple first version.

A future implementation can make confidence more meaningful by
incorporating:

-   parser consistency
-   validation coverage
-   ambiguity detection
-   execution success
-   benchmark accuracy
-   historical user feedback
-   agreement between multiple candidate plans

------------------------------------------------------------------------

## 12. Error Handling Philosophy

The engine follows an important principle:

> **Fail explicitly rather than silently returning an invented result.**

Examples include:

### Missing environment variable

``` text
GROQ_API_KEY is not set.
```

### Unsupported metric

``` text
Unsupported metric: ...
```

### Unsupported dimension

``` text
Unsupported dimension: ...
```

### Insufficient historical data

``` text
At least two years of data are required.
```

### Invalid LLM output

The Pydantic validation layer rejects malformed query plans before
execution.

------------------------------------------------------------------------

## 13. Setup

### 13.1 Clone the repository

``` bash
git clone <repository-url>
cd analytics-engine
```

------------------------------------------------------------------------

### 13.2 Create a virtual environment

Windows:

``` bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

``` bash
python -m venv venv
source venv/bin/activate
```

------------------------------------------------------------------------

### 13.3 Install dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

### 13.4 Configure the Groq API key

Create a `.env` file in the project root:

``` env
GROQ_API_KEY=your_groq_api_key_here
```

Do not commit `.env` to Git.

The repository's `.gitignore` already excludes it.

------------------------------------------------------------------------

## 14. Running the Application

From the project root:

``` bash
python -m app.main
```

You will be prompted:

``` text
Enter your analytics query:
```

Example:

``` text
Enter your analytics query: Total sales in India for March
```

The application prints:

``` text
============================================================
QUERY
============================================================

Total sales in India for March

============================================================
PLAN
============================================================

...

============================================================
RESULT
============================================================

...

============================================================
CONFIDENCE
============================================================

...
```

------------------------------------------------------------------------

## 15. Running the Benchmark

The repository includes `test.py`, which runs every query in:

``` text
dataset/nl_queries.json
```

Run:

``` bash
python test.py
```

The output contains the query and its result in JSON-compatible form.

Example:

``` json
{
  "query": "Total sales in India for March",
  "result": [
    {
      "value": 108.0
    }
  ]
}
```

------------------------------------------------------------------------

## 16. Testing

The project uses `pytest` for automated tests.

Run:

``` bash
pytest
```

Tests can be added for:

-   data loading
-   schema validation
-   filter handling
-   aggregation correctness
-   contribution calculations
-   target comparisons
-   time-series calculations
-   ranking operations
-   end-to-end natural-language queries

A recommended testing strategy is to test the deterministic execution
layer separately from the LLM layer.

For example:

``` text
LLM tests
    ↓
Does natural language produce the expected plan?

Executor tests
    ↓
Does a known plan produce the expected result?
```

This separation makes failures easier to diagnose.

------------------------------------------------------------------------

## 17. Example Results

With the current sample dataset:

### Total sales in India for March

The March India transaction has:

``` text
quantity = 1
unit_price = 120
discount = 10%
```

Therefore:

``` text
revenue = 1 × 120 × (1 - 0.10)
        = 108
```

The engine returns:

``` json
[
  {
    "value": 108.0
  }
]
```

------------------------------------------------------------------------

### Average order value by region

The engine calculates regional revenue divided by the number of orders
in each region.

Example output:

``` json
[
  {
    "region": "APAC",
    "avg_order_value": 118.5
  },
  {
    "region": "EMEA",
    "avg_order_value": 799.3333333333334
  }
]
```

------------------------------------------------------------------------

### Sales contribution by category

The engine calculates each category's percentage of total revenue.

Conceptually:

``` text
category revenue / total revenue × 100
```

The result is returned with:

``` text
product_category
revenue
contribution_pct
```

------------------------------------------------------------------------

## 18. Security and Reliability Considerations

The system intentionally avoids executing arbitrary model-generated
code.

The LLM does **not** directly generate:

``` python
eval(...)
exec(...)
```

or unrestricted SQL/Python for execution.

Instead, it generates a constrained data structure.

Additional protections include:

-   Pydantic schema validation
-   explicit metric allowlists
-   explicit dimension allowlists
-   explicit operator allowlists
-   controlled pandas execution
-   environment-based API-key configuration
-   `.gitignore` protection for secrets

The model should therefore be treated as an **intent parser**, not as a
trusted program generator.

------------------------------------------------------------------------

## 19. Design Decisions

### Decision 1 --- Pandas instead of generated SQL

The dataset is small and tabular, making pandas a simple and transparent
execution backend.

The same query-plan abstraction could later be translated into SQL for
larger datasets.

------------------------------------------------------------------------

### Decision 2 --- LLM + deterministic execution

The LLM is useful for interpreting ambiguous language, while
deterministic code is better suited to executing calculations.

This separation gives the system both:

-   natural-language flexibility
-   reproducible analytical execution

------------------------------------------------------------------------

### Decision 3 --- Data dictionary as semantic grounding

The data dictionary gives the model a controlled vocabulary.

For example:

``` text
sales → revenue
AOV → average order value
orders → count(order_id)
```

This reduces ambiguity and keeps the parser aligned with the dataset.

------------------------------------------------------------------------

### Decision 4 --- Explicit unsupported-data errors

If the dataset cannot answer a question, the engine should say so.

For example, the sample dataset only contains 2024 data. Therefore, a
YoY calculation requiring 2023 cannot legitimately be computed.

------------------------------------------------------------------------

## 20. Current Limitations

The current version is an intentionally lightweight prototype.

### Advanced ranking

Queries involving nested ranking, such as:

``` text
Revenue of top 3 customers per region
```

require a richer query-plan representation than simple aggregation.

The architecture is designed to support this through explicit ranking
semantics rather than hard-coded natural-language string matching.

### Small sample dataset

The included dataset is small and mainly intended for demonstrating the
query engine.

A production implementation would need to consider:

-   large datasets
-   incremental loading
-   query caching
-   database execution
-   distributed processing

### Confidence model

The current confidence score is heuristic rather than statistically
calibrated.

### Limited query language

Only predefined analytical operations are supported.

Future versions can extend the schema with:

-   ranking
-   window functions
-   nested aggregations
-   date ranges
-   rolling metrics
-   percent change
-   conditional metrics
-   multiple filters
-   joins
-   more complex time-series operations

### LLM dependency

Natural-language parsing currently depends on access to the configured
Groq API.

The deterministic executor itself does not require an LLM once a valid
query plan is available.

------------------------------------------------------------------------

## 21. Future Improvements

Potential next steps include:

### 1. Richer query-plan schema

Add explicit structures for:

``` text
ranking
partitioning
nested aggregation
window functions
post-aggregation
```

------------------------------------------------------------------------

### 2. Better confidence estimation

Combine:

``` text
schema validity
+ semantic validation
+ ambiguity detection
+ execution success
+ historical feedback
```

------------------------------------------------------------------------

### 3. Feedback loop

A future `feedback_log.csv` can store:

``` text
query
generated_plan
result
user_feedback
corrected_plan
```

This can be used to identify recurring parser failures and improve
prompts or parsing strategies.

------------------------------------------------------------------------

### 4. Query explanation

The system can return a human-readable explanation such as:

``` text
I interpreted "sales" as revenue, filtered the data to India
and March 2024, and calculated the sum of revenue.
```

This makes the system easier to audit.

------------------------------------------------------------------------

### 5. Database backend

For larger datasets, the controlled query plan could be compiled into
SQL instead of pandas operations:

``` text
Natural Language
      ↓
Query Plan
      ↓
Validation
      ↓
SQL Compiler
      ↓
Database
```

The important abstraction would remain the same.

------------------------------------------------------------------------

### 6. Caching

Repeated natural-language queries could cache their parsed plans and/or
results.

For example:

``` text
"Total sales in India for March"
```

does not necessarily need to be sent to the LLM every time.

------------------------------------------------------------------------

### 7. API layer

The current project exposes the core functionality through Python.

A future version could expose:

``` text
POST /query
```

with:

``` json
{
  "query": "Total sales in India for March"
}
```

and return:

``` json
{
  "query": "...",
  "plan": {...},
  "result": [...],
  "confidence": 0.9
}
```

------------------------------------------------------------------------

## 22. Example End-to-End Flow

For:

``` text
Top 2 cities by profit
```

the complete flow is:

``` text
User
 │
 │ "Top 2 cities by profit"
 ▼
LLM Parser
 │
 │ structured JSON
 ▼
Pydantic QueryPlan
 │
 │ validated plan
 ▼
Validator
 │
 │ valid
 ▼
Confidence Calculator
 │
 │ confidence score
 ▼
Query Executor
 │
 │ pandas groupby + aggregation
 ▼
Result
 │
 ▼
[
  {
    "city": "New York",
    "profit": 200
  },
  {
    "city": "San Francisco",
    "profit": 180
  }
]
```

The model never directly executes the aggregation.

------------------------------------------------------------------------

## 23. Core Design Principle

The most important architectural decision in this project is the
separation of concerns:

``` text
┌───────────────────────────────┐
│       Natural Language        │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       GenAI / LLM Parser      │
│   Language → Structured Plan  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Pydantic Schema         │
│        Structure Check        │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          Validator            │
│     Semantic Constraints      │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│      Confidence Layer         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Query Executor          │
│       Controlled Pandas       │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Analytical Result      │
└───────────────────────────────┘
```

This architecture allows GenAI to provide flexible natural-language
understanding without giving the model unrestricted control over data
execution.

------------------------------------------------------------------------

## 24. License

This project is intended as a take-home / demonstration project.

Add an appropriate license here if the repository is later released
publicly.
