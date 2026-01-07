from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from typing import List
import tempfile
import shutil
import logging

from app.schemas.request import GenerateAssessmentRequest
from app.services.content_resolver import ContentResolver
from app.pipelines.text_pipeline import TextPipeline
from app.services.llm_assessment_service import LLMAssessmentService
from app.services.asr_service import ASRService


router = APIRouter()
logger = logging.getLogger(__name__)

# Instantiate shared services
content_resolver = ContentResolver()
text_pipeline = TextPipeline()
llm_service = LLMAssessmentService()
asr_service = ASRService()



@router.post("/generate-assessment")
async def generate_assessment(request: GenerateAssessmentRequest):
    """
    Full assessment generation endpoint (JSON).
    Accepts inline text or URI content.
    """
    try:
        resolved_type, payload = content_resolver.resolve(
            request.content_type, request.content_source
        )
    except Exception as e:
        logger.error(f"Failed to resolve content: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch content: {e}")

    # Convert content to clean text
  # ------------------------------
# Step 2: Convert content to clean text
# ------------------------------
    try:
        if resolved_type == "text":
            raw_text = payload

        elif resolved_type == "video":
            # NEW: ASR integration
            raw_text = asr_service.transcribe(payload)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown content type: {resolved_type}")

    except Exception as e:
        logger.error(f"Failed to process content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


    # Clean text & create sections
    try:
        sections = text_pipeline.run(raw_text)
    except Exception as e:
        logger.error(f"Failed to clean transcript: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean transcript: {e}")

    # Generate assessment questions
    try:
        questions = llm_service.generate_questions(
            sections,
            questions_per_section=request.total_questions // max(len(sections), 1),
        )
    except Exception as e:
        logger.error(f"LLM question generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"LLM question generation failed: {e}"
        )

    # Format response
    response = {
        "assessment_id": "ASMT-001",
        "course_id": request.course_id,
        "module_id": request.module_id,
        "metadata": {
            "content_type": request.content_type,
            "total_questions": len(questions),
            "generated_at": "2026-01-05T12:00:00Z",
        },
        "sections": [
            {"section_id": s.section_id, "title": s.title, "content": s.content}
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

    return response


@router.post("/generate-assessment/upload")
async def generate_assessment_with_file(
    file: UploadFile = File(...),
    course_id: str = None,
    module_id: str = None,
    content_type: str = "text",
    total_questions: int = 4,
):
    """
    Assessment generation endpoint with file upload.
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            file_path = tmp.name

        resolved_type = "video" if content_type == "video" else "text"
        payload = file_path
    except Exception as e:
        logger.error(f"Failed to process upload: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process file: {e}")

    # Convert content to clean text
    try:
        if resolved_type == "text":
            with open(payload, "r") as f:
                raw_text = f.read()
        elif resolved_type == "video":
            raise NotImplementedError(
                "Video ASR not implemented yet. Use transcript for now."
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown content type: {resolved_type}"
            )
    except Exception as e:
        logger.error(f"Failed to process content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process content: {e}")

    # Clean text & create sections
    try:
        sections = text_pipeline.run(raw_text)
    except Exception as e:
        logger.error(f"Failed to clean transcript: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean transcript: {e}")

    # Generate assessment questions
    try:
        questions = llm_service.generate_questions(
            sections, questions_per_section=total_questions // max(len(sections), 1)
        )
    except Exception as e:
        logger.error(f"LLM question generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"LLM question generation failed: {e}"
        )

    # Format response
    response = {
        "assessment_id": "ASMT-001",
        "course_id": course_id,
        "module_id": module_id,
        "metadata": {
            "content_type": content_type,
            "total_questions": len(questions),
            "generated_at": "2026-01-05T12:00:00Z",
        },
        "sections": [
            {"section_id": s.section_id, "title": s.title, "content": s.content}
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

    return response
