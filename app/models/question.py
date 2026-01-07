from dataclasses import dataclass
from typing import List


@dataclass
class Question:
    """
    Represents a single assessment question.
    """
    question_id: str
    section_id: str
    type: str  # e.g., 'mcq' or 'short_answer'
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
