from typing import List
from app.models.section import Section
from app.services.cleaning_service import TranscriptCleaner


class TextPipeline:
    """
    Handles text-based content (including transcripts).
    """

    def __init__(self):
        self.cleaner = TranscriptCleaner()

    def run(self, raw_text: str) -> List[Section]:
        """
        Full text pipeline:
        raw text -> transcript -> sections
        """
        transcript = self.cleaner.to_transcript(raw_text)
        sections = self.cleaner.to_sections(transcript)
        return sections
