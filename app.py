import os
import logging
import requests
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("goings-os-core")

app = FastAPI(title="Goings OS Core Engine", version="3.0.0")

class GHLInboundPayload(BaseModel):
    source: Optional[str] = "GHL_Workflow_Lead_Ingest"
    contact_id: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    business_sector: Optional[str] = None
    intake_notes: Optional[str] = None
    action_required: Optional[str] = "qualify_and_generate_proposal"

@app.get("/healthz")
def liveness_probe():
    return {"status": "HEALTHY"}

@app.get("/ready")
def readiness_probe():
    return {"status": "READY", "system": "Goings OS Core Engine"}

@app.post("/query")
def process_ghl_query(payload: GHLInboundPayload):
    logger.info(f"Processing query for {payload.contact_name}")
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY environment variable is empty or not mounted in container."
        )

    prompt_text = f"""
    System Role: Goings OS Core Ingestion Engine.
    Task: Analyze incoming lead payload and generate an executive intake brief.

    Client Details:
    * Name: {payload.contact_name}
    * Company: {payload.business_sector}
    * Notes: {payload.intake_notes}
    * Requested Action: {payload.action_required}

    Instructions:
    1. Evaluate lead qualification level (High, Medium, Low).
    2. Draft a 3 step immediate action plan for Goings OS.
    3. Maintain clean markdown format with no em dashes.
    """

    # Verified active models from live key diagnostics
    candidate_models = [
        "models/gemini-3.6-flash",
        "models/gemini-3.5-flash",
        "models/gemini-3.1-flash-lite"
    ]

    req_body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }

    last_error = None

    for model_path in candidate_models:
        gen_url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={api_key}"
        logger.info(f"Sending direct REST request to modern endpoint: {model_path}")
        
        try:
            res = requests.post(gen_url, json=req_body, headers={"Content-Type": "application/json"}, timeout=30)
            
            if res.status_code == 200:
                res_data = res.json()
                output_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"Successfully generated response via modern model: {model_path}")
                return {
                    "status": "SUCCESS",
                    "provider": f"Direct REST API ({model_path})",
                    "contact_id": payload.contact_id,
                    "contact_name": payload.contact_name,
                    "engine": "goings-os-core",
                    "analysis_output": output_text
                }
            else:
                last_error = f"HTTP {res.status_code}: {res.text}"
                logger.warning(f"Model candidate '{model_path}' failed: {last_error}")
        except Exception as err:
            last_error = str(err)
            logger.warning(f"Model candidate '{model_path}' exception: {last_error}")

    raise HTTPException(
        status_code=500,
        detail=f"All modern model endpoints failed. Last error: {last_error}"
    )
