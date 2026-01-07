from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import tempfile
import shutil
import logging

from app.schemas.request import GenerateAssessmentRequest
from app.services.content_resolver import ContentResolver
from app.pipelines.text_pipeline import TextPipeline
from app.services.llm_assessment_service import LLMAssessmentService
from app.models.question import Question
from fastapi import APIRouter, HTTPException
from app.services.assessment_pipeline_service import AssessmentPipeline


router = APIRouter()
logger = logging.getLogger(__name__)

# Instantiate shared services
content_resolver = ContentResolver()
text_pipeline = TextPipeline()
llm_service = LLMAssessmentService()
pipeline = AssessmentPipeline()


@router.post("/generate-assessment")
def generate_assessment(payload: dict):
    try:
        return pipeline.run(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/generate-assessment")
async def generate_assessment(
    request: GenerateAssessmentRequest,
    file: UploadFile = File(None),  # optional, only for direct uploads
):
    """
    Full assessment generation endpoint.
    Accepts:
        - inline text
        - URI (e.g., Azure Blob)
        - optional direct file upload
    """

    # ------------------------------
    # Step 1: Resolve content
    # ------------------------------
    try:
        if file:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                shutil.copyfileobj(file.file, tmp)
                file_path = tmp.name
            resolved_type = "video" if request.content_type == "video" else "text"
            payload = file_path
        else:
            resolved_type, payload = content_resolver.resolve(
                request.content_type, request.content_source
            )
    except Exception as e:
        logger.error(f"Failed to resolve content: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch content: {e}")

    # ------------------------------
    # Step 2: Convert content to clean text
    # ------------------------------
    try:
        if resolved_type == "text":
            raw_text = payload
        elif resolved_type == "video":
            # For POC: simulate ASR or plug in actual ASR here
            # Here we just raise NotImplementedError for now
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

    # ------------------------------
    # Step 3: Clean text & create sections
    # ------------------------------
    try:
        sections = text_pipeline.run(raw_text)
    except Exception as e:
        logger.error(f"Failed to clean transcript: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean transcript: {e}")

    # ------------------------------
    # Step 4: Generate assessment questions
    # ------------------------------
    try:
        questions: List[Question] = llm_service.generate_questions(
            sections,
            questions_per_section=request.total_questions // max(len(sections), 1),
        )
    except Exception as e:
        logger.error(f"LLM question generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"LLM question generation failed: {e}"
        )

    # ------------------------------
    # Step 5: Format response
    # ------------------------------
    response = {
        "assessment_id": "ASMT-001",  # TODO: generate unique ID in production
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
