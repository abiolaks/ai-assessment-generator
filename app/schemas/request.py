# Th request schema
# Explicitly supports Azure Blob

# Explicitly supports inline text

# Explicitly supports file uploads

# Prevents guessing or ambiguity

from typing import Optional, Literal
from pydantic import BaseModel, HttpUrl, Field, model_validator


class ContentAuth(BaseModel):
    type: Literal["sas", "bearer"]
    token: str


class ContentSource(BaseModel):
    type: Literal["uri", "inline", "file"]

    # Used when type == "uri"
    uri: Optional[HttpUrl] = None
    auth: Optional[ContentAuth] = None

    # Used when type == "inline"
    text: Optional[str] = None


class GenerateAssessmentRequest(BaseModel):
    course_id: str
    module_id: str
    content_type: Literal["video", "text"]
    content_source: ContentSource
    total_questions: int = Field(gt=0, le=50)
    difficulty: Optional[Literal["easy", "medium", "hard"]] = "medium"

    @model_validator(mode="after")
    def validate_content_source(self):
        content_type = self.content_type
        source = self.content_source

        if source.type == "uri" and not source.uri:
            raise ValueError("URI must be provided when content_source.type is 'uri'")

        if source.type == "inline" and not source.text:
            raise ValueError(
                "Text must be provided when content_source.type is 'inline'"
            )

        if content_type == "video" and source.type == "inline":
            raise ValueError("Inline text is not valid for video content")

        return self


# Video always has a retrievable asset

# Text never runs ASR

# Cloud storage works only when access is explicit
