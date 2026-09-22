import json
import os

from groq import Groq

from .schemas import QueryPlan


class LLMQueryParser:

    def __init__(self, data_dictionary):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add it to your .env file."
            )

        self.client = Groq(api_key=api_key)
        self.data_dictionary = data_dictionary

    def parse(self, query):

        system_prompt = f"""
You are an analytics query parser.

Your job is to convert a natural-language business
analytics question into a structured JSON query plan.

You MUST only use metrics and dimensions defined
in the data dictionary.

DATA DICTIONARY:
{json.dumps(self.data_dictionary, indent=2)}

AVAILABLE METRICS:
{json.dumps(self.data_dictionary["metrics"], indent=2)}

AVAILABLE DIMENSIONS:
{json.dumps(self.data_dictionary["dimensions"], indent=2)}

IMPORTANT RULES:

1. "sales", "income" means revenue.
2. Revenue is:
   quantity * unit_price * (1 - discount)
3. Profit means the profit column.
4. Orders means count(order_id).
5. AOV means revenue / count(order_id).
6. "by X" means GROUP BY X.
7. "top N" means sort descending and limit N.
8. "bottom N" means sort ascending and limit N.
9. A month such as March 2024 should be represented
   as a filter on the month column using YYYY-MM.
10. For contribution percentage, use operation "contribution".
11. For target questions, use operation "target_comparison".
12. For year-over-year questions, use operation "yoy".

Return ONLY valid JSON.

The JSON must follow this structure:

{{
  "metric": "revenue",
  "operation": "sum",
  "group_by": [],
  "filters": [],
  "sort": null,
  "limit": null
}}
"""

        user_prompt = f"""
Convert this query into the required structured plan:

{query}
"""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code fences if the model adds them
        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        parsed = json.loads(content)

        return QueryPlan(**parsed)