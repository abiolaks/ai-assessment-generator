# Convert Video to Transcript( Whisper)
"""
ASR Service
-----------
Responsible for converting video/audio files into raw text.
This service is isolated so it can be swapped later (Azure, Whisper, etc.).
"""

import whisper
import os

from pathlib import Path


class ASRService:
    def __init__(self, model):
        self.model = model

    def transcribe(self, media_path: str) -> str:
        """
        Transcribes audio or video file to text.
        """

        # CRITICAL FIX: ensure string path
        if isinstance(media_path, Path):
            media_path = str(media_path)

        result = self.model.transcribe(media_path)
        return result["text"]
