# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: MEDIA TRANSCRIPTION AND CLEANING TRANSFORMER
# BIND: UTILS GATEWAY // DATA STORAGE
# COMPLIANCE: ZERO EM-DASHES ENFORCED // ALWAYS POSITIVE // EXPLICIT TYPING
# ==============================================================================

import os
import re
from pathlib import Path

class MediaTransformer:
    def __init__(self, storage_dir: str = "data/transcripts"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def clean_transcript(self, raw_text: str) -> str:
        # Remove video timestamp signatures like [00:12:34] or 12:34
        clean_text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', raw_text)
        # Normalize multiple spaces and line breaks
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()

    def store_asset(self, file_name: str, raw_text: str) -> str:
        cleaned_payload = self.clean_transcript(raw_text)
        target_path = self.storage_dir / f"{file_name}.txt"
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(cleaned_payload)
            
        return str(target_path)
