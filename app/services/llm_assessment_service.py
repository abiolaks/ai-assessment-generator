"""
LLM Assessment Service
---------------------
Uses Ollama to generate assessment questions from cleaned transcript sections.
Falls back safely if LLM fails.
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
        """
        all_questions = []

        for section in sections:
            try:
                prompt = self._build_prompt(section, questions_per_section)
                response = self._call_llm(prompt)
                questions = self._parse_response(response, section.section_id)
                all_questions.extend(questions)

            except Exception as e:
                logger.error(f"LLM failed for section {section.section_id}: {e}")
                all_questions.extend(
                    self._fallback_questions(section, questions_per_section)
                )

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
Generate {n} multiple-choice questions.

RULES:
- Base questions ONLY on the section content
- Each question must have 4 options
- Provide the correct answer
- Provide a short explanation based on the section
- Use ONLY the content above.
- DO NOT use external knowledge.
- Each question must be answerable directly from the content.
- Exactly 4 options (A, B, C, D).
- Only ONE correct option.
- Incorrect options must be clearly wrong.
- No duplicate or overlapping options.
- Avoid vague or generic wording.

OUTPUT FORMAT (JSON ONLY):
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
        """
        Robust Ollama call that avoids Windows Unicode decoding issues.
        """
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

            return self._extract_json(raw_output)

        except Exception as e:
            raise RuntimeError(f"Ollama call failed: {e}")

    # -----------------------------
    # Response Parser
    # -----------------------------
    def _parse_response(self, data: dict, section_id: str) -> List[Question]:
        questions = []

        for idx, q in enumerate(data.get("questions", []), start=1):
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

    # Extract Json
    def _extract_json(self, text: str) -> dict:
        """
        Extract the first valid JSON object from LLM output.
        This protects against extra text, markdown, or explanations.
        """

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("No valid JSON object found in LLM output")

        json_str = text[start : end + 1]

        return json.loads(json_str)

    # -----------------------------
    # Fallback (VERY IMPORTANT)
    # -----------------------------
    def _fallback_questions(self, section: Section, n: int) -> List[Question]:
        """
        Ensures pipeline never breaks if LLM fails.
        """
        return [
            Question(
                question_id=f"{section.section_id}-FB-{i}",
                section_id=section.section_id,
                type="mcq",
                question=f"What is a key concept in '{section.title}'?",
                options=["Option A", "Option B", "Option C", "Option D"],
                correct_answer="Option A",
                explanation="This is a fallback question due to LLM failure.",
            )
            for i in range(1, n + 1)
        ]
