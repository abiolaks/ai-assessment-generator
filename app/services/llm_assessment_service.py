"""
LLM Assessment Service
---------------------
Uses Ollama to generate assessment questions from cleaned transcript sections.
Strict JSON-only output. No fallbacks.
"""

import json
import subprocess
import logging
from typing import List

from app.models.section import Section
from app.models.question import Question

logger = logging.getLogger(__name__)


class LLMAssessmentService:
    def __init__(self, model_name: str = "qwen3:0.6b"):
        self.model_name = model_name

    def generate_questions(
        self, sections: List[Section], questions_per_section: int = 1
    ) -> List[Question]:
        """
        Generate assessment questions using LLM.
        Raises on failure so pipeline can skip sections.
        """
        all_questions: List[Question] = []

        for section in sections:
            prompt = self._build_prompt(section, questions_per_section)
            response = self._call_llm(prompt)
            questions = self._parse_response(response, section.section_id)

            if not questions:
                raise ValueError("LLM returned empty question set")

            all_questions.extend(questions)

        return all_questions

    # -----------------------------
    # Prompt Builder
    # -----------------------------
    def _build_prompt(self, section: Section, n: int) -> str:
        return f"""
You are an assessment generator.

SECTION ID: {section.section_id}
SECTION TITLE: {section.title}
SECTION CONTENT:
{section.content}

TASK:
Generate exactly {n} multiple-choice questions.

STRICT RULES (MANDATORY):
- Use ONLY the section content
- Exactly 4 options per question (A, B, C, D)
- Only ONE correct answer
- All incorrect options must be clearly wrong
- No vague or generic wording
- No duplicate options
- No external knowledge
- NO explanations outside JSON
- NO markdown
- NO commentary
- NO text before or after JSON

OUTPUT FORMAT (JSON ONLY — NO OTHER TEXT):
{{
  "questions": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "explanation": "..."
    }}
  ]
}}
"""

    # -----------------------------
    # Ollama Call
    # -----------------------------
    def _call_llm(self, prompt: str) -> dict:
        try:
            process = subprocess.Popen(
                ["ollama", "run", self.model_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout_bytes, stderr_bytes = process.communicate(
                input=prompt.encode("utf-8")
            )

            if process.returncode != 0:
                raise RuntimeError(stderr_bytes.decode("utf-8", errors="ignore"))

            raw_output = stdout_bytes.decode("utf-8", errors="ignore")

            return self._extract_and_validate_json(raw_output)

        except Exception as e:
            raise RuntimeError(f"Ollama call failed: {e}")

    # -----------------------------
    # JSON Extraction + Validation
    # -----------------------------
    def _extract_and_validate_json(self, text: str) -> dict:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("No valid JSON object found in LLM output")

        json_str = text[start : end + 1]

        data = json.loads(json_str)

        # HARD validation
        if "questions" not in data or not isinstance(data["questions"], list):
            raise ValueError("Invalid JSON: 'questions' must be a list")

        for q in data["questions"]:
            for field in ("question", "options", "correct_answer", "explanation"):
                if field not in q:
                    raise ValueError(f"Missing field '{field}' in question")

            if not isinstance(q["options"], list) or len(q["options"]) != 4:
                raise ValueError("Each question must have exactly 4 options")

        return data

    # -----------------------------
    # Response Parser
    # -----------------------------
    def _parse_response(self, data: dict, section_id: str) -> List[Question]:
        questions: List[Question] = []

        for idx, q in enumerate(data["questions"], start=1):
            questions.append(
                Question(
                    question_id=f"{section_id}-Q{idx}",
                    section_id=section_id,
                    type="mcq",
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct_answer"],
                    explanation=q["explanation"],
                )
            )

        return questions
