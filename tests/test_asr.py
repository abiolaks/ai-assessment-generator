import sys
from pathlib import Path

# Add parent directory to path so app module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.asr_service import ASRService

asr = ASRService()

# Use absolute path - replace with actual path to your audio file
audio_file = r"C:\Users\AbiolaLawani\workspace\lms_assessement_generator\ai-assessment-generator\sample.mp3"

text = asr.transcribe(audio_file)

print("\nTRANSCRIPT:")
print(text)
