# Remove noise from raw transcripts
# NOrmalize text
# Section Segmentation
import re
from typing import List
from app.models.transcript import Transcript, TranscriptSegment
from app.models.section import Section


class TranscriptCleaner:
    """
    Cleans raw transcript text and splits it into logical sections.
    """

    def clean_text(self, text: str) -> str:
        """
        Perform basic text normalization.
        This must be safe and deterministic.
        """
        if not text:
            return ""

        # Lower risk operations only
        text = text.strip()
        text = re.sub(r"\s+", " ", text)  # normalize whitespace
        text = re.sub(
            r"\b(um|uh|you know|uumh|Uh-huh)\b", "", text, flags=re.IGNORECASE
        )
        text = text.strip()

        return text

    def to_transcript(self, raw_text: str) -> Transcript:
        """
        Convert raw text into transcript segments.
        For now, split by sentences.
        """
        if not raw_text:
            raise ValueError("Raw text is empty")

        sentences = re.split(r"(?<=[.!?])\s+", raw_text)

        segments = [
            TranscriptSegment(text=self.clean_text(sentence))
            for sentence in sentences
            if sentence.strip()
        ]

        return Transcript(segments=segments)

    def to_sections(
        self, transcript: Transcript, max_sentences_per_section: int = 2
    ) -> List[Section]:
        """
        Group transcript segments into logical sections.
        Simple, deterministic grouping.
        """

        sections: List[Section] = []
        buffer: List[str] = []
        section_index = 1

        for segment in transcript.segments:
            buffer.append(segment.text)

            if len(buffer) >= max_sentences_per_section:
                sections.append(
                    Section(
                        section_id=f"S{section_index}",
                        title=f"Section {section_index}",
                        content=" ".join(buffer),
                    )
                )
                buffer = []
                section_index += 1

        # Handle remaining text
        if buffer:
            sections.append(
                Section(
                    section_id=f"S{section_index}",
                    title=f"Section {section_index}",
                    content=" ".join(buffer),
                )
            )

        return sections
