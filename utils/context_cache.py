# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: VERTEX AI CONTEXT CACHING UTILITY
# COMPLIANCE: ZERO EM-DASHES; EXPLICIT TYPING; ALWAYS POSITIVE
# ==============================================================================

import os
from google import genai
from google.genai import types
from typing import Optional, Any

class VertexContextCache:
    """Manages cached context payloads for Vertex AI Gemini models to reduce token consumption."""

    def __init__(self):
        self.client = genai.Client()
        self.default_model = "gemini-1.5-flash-001"

    def create_cache(self, contents: list, ttl_seconds: int = 300, display_name: Optional[str] = None) -> Any:
        """Creates a context cache for large documents or system instructions."""
        config = types.CreateCachedContentConfig(
            contents=contents,
            ttl=f"{ttl_seconds}s",
            display_name=display_name
        )
        cache = self.client.caches.create(
            model=self.default_model,
            config=config
        )
        return cache

    def get_cache(self, cache_name: str) -> Any:
        """Retrieves active cached content by identifier."""
        return self.client.caches.get(name=cache_name)

    def delete_cache(self, cache_name: str) -> None:
        """Deletes cached content to release budget resources."""
        self.client.caches.delete(name=cache_name)
