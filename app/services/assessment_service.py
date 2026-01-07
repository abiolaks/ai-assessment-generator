# Prompt LLM
# Generate  questions and Answers
from typing import List
from app.models.section import Section
from app.models.question import Question


class AssessmentService:
    """
    Generates assessment questions from sections.
    This stub generates simple placeholder questions.
    """

    def generate_questions(
        self, sections: List[Section], questions_per_section: int = 1
    ) -> List[Question]:
        """
        For each section, generate a fixed number of placeholder questions.
        Later, replace with LLM logic.
        """
        question_list: List[Question] = []
        q_index = 1

        for section in sections:
            for _ in range(questions_per_section):
                question_list.append(
                    Question(
                        question_id=f"Q{q_index}",
                        section_id=section.section_id,
                        type="mcq",
                        question=f"Placeholder question for {section.title}",
                        options=["Option A", "Option B", "Option C", "Option D"],
                        correct_answer="Option A",
                        explanation=f"This is a placeholder explanation from {section.title}.",
                    )
                )
                q_index += 1

        return question_list
