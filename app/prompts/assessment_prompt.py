def build_assessment_prompt(section_text: str, num_questions: int) -> str:
    return f"""
SOURCE TEXT:
{section_text}

TASK:
Generate {num_questions} multiple-choice questions.

RULES:
- Use ONLY the source text
- Each question must have 4 options
- Exactly ONE correct answer
- Short explanation based only on the text

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "questions": [
    {{
      "question": "string",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A",
      "explanation": "string"
    }}
  ]
}}

CRITICAL:
- Return ONLY valid JSON
- No markdown
- No commentary
- No trailing text
"""
