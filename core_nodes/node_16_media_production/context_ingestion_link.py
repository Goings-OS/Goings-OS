# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: CONTEXT CACHING INGESTION LINK
# BIND: NODE 16 MEDIA PRODUCTION // COGNITIVE GATEWAY
# COMPLIANCE: ZERO EM-DASHES ENFORCED // ALWAYS POSITIVE // EXPLICIT TYPING
# ==============================================================================

import google.generativeai as genai
from utils.context_cache import VertexContextCache

class ContextIngestionLink:
    def __init__(self, model_name: str = "models/gemini-1.5-flash"):
        self.model_name = model_name

    def process_targeted_block(self, block_file_path: str, cached_content_id: str) -> str:
        with open(block_file_path, "r", encoding="utf-8") as f:
            specific_block_data = f.read()

        # Connect to the model using the pre cached system framework rules
        model_instance = genai.GenerativeModel(model_name=self.model_name)
        
        # Pass the individual block text as a targeted instruction
        query_instruction = f"Analyze this specific structured block data and extract conversion triggers: {specific_block_data}"
        
        response = model_instance.generate_content(
            query_instruction,
            version="v1beta",
            config={"cached_content": cached_content_id}
        )
        
        return response.text
