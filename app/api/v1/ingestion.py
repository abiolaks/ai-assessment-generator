from fastapi import APIRouter

router = APIRouter()


@router.post("/ingest")
async def ingest_content():
    """Ingest content endpoint"""
    return {"message": "Ingest content endpoint"}
