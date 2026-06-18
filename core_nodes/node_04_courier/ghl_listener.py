import json
import sqlite3
from fastapi import FastAPI, Request, HTTPException

app = FastAPI(title="Goings OS GHL Production Listener")

@app.post("/webhook/ghl/transaction")
async def receive_ghl_webhook(request: Request):
    payload = await request.json()
    
    # Extract data from the GHL webhook object
    gross_amount = payload.get("amount", 0.0)
    net_allocation = gross_amount * 0.5  # Standard 50% split governance
    source = "GHL_PRODUCTION_WEBHOOK"
    
    # Write to local vault
    conn = sqlite3.connect('goings_os_vault.db')
    c = conn.cursor()
    c.execute("""
        INSERT INTO owners_draw_allocations (source_origin, gross_amount, net_allocation, tracking_status)
        VALUES (?, ?, ?, ?)
    """, (source, gross_amount, net_allocation, "VERIFIED_PRODUCTION"))
    conn.commit()
    conn.close()
    
    return {"status": "SUCCESS", "message": "Transaction routed to vault"}
