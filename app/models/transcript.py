from typing import List
from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    """
    Represents a small unit of transcript text.
    For video, this may come from ASR timestamps.
    For text, this may be a paragraph.
    """
    text: str


@dataclass
class Transcript:
    """
    Represents the full transcript after ingestion.
    """
    segments: List[TranscriptSegment]
