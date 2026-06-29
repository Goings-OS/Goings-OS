# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: PRIVATE KERNEL GATEWAY ENTRYPOINT
# COMPLIANCE: ZERO EM-DASHES; EXPLICIT TYPING; ALWAYS POSITIVE
# ==============================================================================

import os
from fastapi import FastAPI
from middleware.token_counter import TokenCounterMiddleware
from typing import Dict

app = FastAPI(title="Goings OS Gateway Engine")

# Bind token budget tracker middleware to intercept Port 5000 traffic
app.add_middleware(TokenCounterMiddleware, db_path="/app/data/private_kernel.db")

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"status": "SUCCESS", "message": "Goings OS Private Kernel Gateway active"}

@app.post("/api/chat")
async def chat_endpoint(payload: Dict[str, str]) -> Dict[str, str]:
    return {
        "status": "SUCCESS",
        "reply": "Message processed under token budget governance control"
    }
