from pathlib import Path
from app.services.assessment_pipeline_service import AssessmentPipeline

# ------------------------------
# Validate local video exists
# ------------------------------
video_path = Path(".\sample2.mp4")

if not video_path.exists():
    raise FileNotFoundError(f"Video not found: {video_path}")

# ------------------------------
# Build payload
# ------------------------------
payload = {
    "course_id": "ML101",
    "module_id": "M1",
    "content_type": "video",
    "content_source": {
        "type": "local",  # IMPORTANT
        "path": video_path,
    },
    "total_questions": 4,
}

# ------------------------------
# Run pipeline
# ------------------------------
pipeline = AssessmentPipeline()
result = pipeline.run(payload)

print("\n=== PIPELINE OUTPUT ===")
print(result)
