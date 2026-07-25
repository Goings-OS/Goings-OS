import os
import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import google.generativeai as genai

# Configure Enterprise Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("goings-os-core")

app = FastAPI(
    title="Goings-OS Enterprise Core Engine",
    description="Autonomous Enterprise Command API for Goings OS",
    version="1.0.0"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AgentQuery(BaseModel):
    prompt: str
    model: str = "gemini-1.5-flash"

@app.get("/healthz", status_code=status.HTTP_200_OK)
def liveness_probe():
    """Liveness probe for Cloud Run health checks."""
    return {"status": "HEALTHY"}

@app.get("/ready", status_code=status.HTTP_200_OK)
def readiness_probe():
    """Readiness probe for traffic routing."""
    return {
        "status": "READY",
        "system": "Goings OS Core Engine",
        "environment": "Enterprise Production",
        "region": os.getenv("K_SERVICE", "us-west1")
    }

@app.post("/query")
def process_query(payload: AgentQuery):
    logger.info(f"Processing query using model: {payload.model}")
    try:
        if GEMINI_API_KEY:
            model = genai.GenerativeModel(payload.model)
            response = model.generate_content(payload.prompt)
            output_text = response.text
        else:
            output_text = f"[Goings-OS Core Engine Response]: Processed prompt -> '{payload.prompt}'"
        
        return {
            "status": "SUCCESS",
            "agent": "Goings-OS-Core",
            "prompt": payload.prompt,
            "response": output_text
        }
    except Exception as e:
        logger.error(f"Execution Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
