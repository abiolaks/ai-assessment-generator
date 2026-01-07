from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.v1 import assessment, health, ingestion
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Assessment Generator",
    description="Generate assessments from text and video content using LLM",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(assessment.router, prefix="/api/v1", tags=["assessment"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["ingestion"])


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up AI Assessment Generator API")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Assessment Generator API")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
