import json
from typing import Any, Dict, List

from models import ReviewAnalysis

SYSTEM_PROMPT = """
You are an expert e-commerce data analyst fluent in German and English.

Analyze German product reviews and return ONLY valid JSON.

Extract:
- score (1-5)
- topics (list of categories like shipping, quality, packaging)
- review_extracted (important words or short phrases)
- is_urgent (boolean)
- issue_reason (short explanation if severe issue exists)
"""


def sanitize_review(text: str) -> str:
    return " ".join(text.split())


def create_analysis_prompt(review_text: str) -> List[Dict[str, str]]:
    review_text = sanitize_review(review_text)
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"""
Analyze this German customer review:

\"\"\"{review_text}\"\"\"

Return JSON only matching the schema.
""",
        },
    ]


def parse_llm_response(content: str) -> Dict[str, Any]:
    return json.loads(content)


def validate_analysis(data: Dict[str, Any]) -> ReviewAnalysis:
    return ReviewAnalysis(**data)


def transform_analysis(llm_response: str) -> ReviewAnalysis:
    data = parse_llm_response(llm_response)
    return validate_analysis(data)
