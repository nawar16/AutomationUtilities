from pydantic import BaseModel
from typing import List


class ReviewAnalysis(BaseModel):
    score: int
    topics: List[str]
    review_extracted: List[str]
    is_urgent: bool
    issue_reason: str