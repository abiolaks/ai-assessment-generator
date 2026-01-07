from app.utils.json_utils import safe_json_loads
from app.prompts.assessment_prompt import build_assessment_prompt

class AssessmentService:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate_questions(self, section_text: str, num_questions: int):
        prompt = build_assessment_prompt(section_text, num_questions)
        response = self.llm.generate(prompt)

        parsed = safe_json_loads(response)

        if not parsed or "questions" not in parsed:
            raise ValueError("Invalid LLM JSON output")

        return parsed["questions"]
