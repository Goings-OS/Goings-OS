import os

# Dynamic Model Alias Configuration
# Automatically binds to Google's latest model endpoints
MODEL_CONFIG = {
    "HEAVY_REASONING": os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
    "HIGH_SPEED_EXEC": os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash"),
    "DEFAULT_TEMPERATURE": 0.2,
    "MAX_OUTPUT_TOKENS": 8192
}

def get_model_for_task(task_type: str) -> str:
    """
    Routes tasks to the optimal Gemini engine.
    """
    heavy_tasks = ["pitch_deck_synthesis", "grant_audit", "code_architecture", "video_storyboard"]
    if task_type in heavy_tasks:
        return MODEL_CONFIG["HEAVY_REASONING"]
    return MODEL_CONFIG["HIGH_SPEED_EXEC"]
