import logging
from typing import Dict, Any, List
import whisper

from app.services.content_resolver import ContentResolver
from app.services.asr_service import ASRService
from app.services.llm_assessment_service import LLMAssessmentService
from app.services.cleaning_service import TranscriptCleaner
from app.models.section import Section
from app.models.question import Question

logger = logging.getLogger(__name__)


class AssessmentPipeline:
    """
    End-to-end orchestration pipeline for assessment generation.

    Flow:
        Resolve content →
        ASR (if video) →
        Clean transcript →
        Sentence segmentation →
        Sectioning →
        LLM question generation →
        Structured response
    """

    def __init__(self):
        self.content_resolver = ContentResolver()
        # Load Whisper ONCE
        whisper_model = whisper.load_model("base")  # or "small"
        self.asr_service = ASRService(whisper_model)

        self.cleaner = TranscriptCleaner()
        self.llm_service = LLMAssessmentService()

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute full pipeline.

        Expected payload:
        {
            "course_id": str,
            "module_id": str,
            "content_type": "text" | "video",
            "content_source": str,  # inline text or URI (Azure Blob)
            "total_questions": int
        }
        """

        logger.info("Starting assessment pipeline")

        # ------------------------------
        # Step 1: Resolve content
        # ------------------------------
        resolved_type, content = self.content_resolver.resolve(
            payload["content_type"],
            payload["content_source"],
        )

        # ------------------------------
        # Step 2: ASR (if video)
        # ------------------------------
        if resolved_type == "video":
            logger.info("Running ASR on video content")
            raw_text = self.asr_service.transcribe(content)
        elif resolved_type == "text":
            raw_text = content
        else:
            raise ValueError(f"Unsupported content type: {resolved_type}")

        if not raw_text.strip():
            raise ValueError("Resolved content is empty after processing")

        # ------------------------------
        # Step 3: Clean + transcript
        # ------------------------------
        logger.info("Cleaning transcript")
        clean_text = self.cleaner.clean_text(raw_text)

        transcript = self.cleaner.to_transcript(clean_text)

        # ------------------------------
        # Step 4: Sectioning / chunking
        # ------------------------------
        sections: List[Section] = self.cleaner.to_sections(transcript)

        if not sections:
            raise ValueError("No sections generated from transcript")

        logger.info(f"Generated {len(sections)} sections")

        # ------------------------------
        # Step 5: LLM assessment generation
        # ------------------------------
        questions_per_section = max(payload["total_questions"] // len(sections), 1)

        questions: List[Question] = self.llm_service.generate_questions(
            sections=sections,
            questions_per_section=questions_per_section,
        )

        if not questions:
            raise ValueError("LLM returned no questions")

        # ------------------------------
        # Step 6: Assemble response
        # ------------------------------
        response = {
            "assessment_id": "ASMT-POC-001",
            "course_id": payload["course_id"],
            "module_id": payload["module_id"],
            "metadata": {
                "content_type": resolved_type,
                "total_sections": len(sections),
                "total_questions": len(questions),
            },
            "sections": [
                {
                    "section_id": s.section_id,
                    "title": s.title,
                    "content": s.content,
                }
                for s in sections
            ],
            "questions": [
                {
                    "question_id": q.question_id,
                    "section_id": q.section_id,
                    "type": q.type,
                    "question": q.question,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                }
                for q in questions
            ],
        }

        logger.info("Assessment pipeline completed successfully")

        return response
