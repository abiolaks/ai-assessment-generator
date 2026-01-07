import sys
from pathlib import Path

# Add parent directory to path so app module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipelines.text_pipeline import TextPipeline
from app.services.assessment_service import AssessmentService


if __name__ == "__main__":
    # Step 1: Get clean sections
    raw_text = """
    Supervised learning uses labeled data to train models.
    It is widely used for classification tasks.
    Unsupervised learning finds patterns in unlabeled data.
    """
    text_pipeline = TextPipeline()
    sections = text_pipeline.run(raw_text)

    # Step 2: Generate questions
    assessment_service = AssessmentService()
    questions = assessment_service.generate_questions(sections, questions_per_section=2)

    # Step 3: Print
    for q in questions:
        print(f"Question ID: {q.question_id}")
        print(f"Section: {q.section_id}")
        print(f"Question: {q.question}")
        print(f"Options: {q.options}")
        print(f"Answer: {q.correct_answer}")
        print(f"Explanation: {q.explanation}")
        print("-" * 50)
