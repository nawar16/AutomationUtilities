from typing import List

from pydantic import BaseModel


class ReviewAnalysis(BaseModel):
    score: int
    topics: List[str]
    review_extracted: List[str]
    is_urgent: bool
    issue_reason: str
