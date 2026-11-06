# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: GHL PRODUCTION WEBHOOK LISTENER (core_nodes/node_04_courier/ghl_listener.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; SQLITE WAL CONCURRENCY
# ==============================================================================

import os
import time
import sqlite3
from fastapi import FastAPI, Request

app = FastAPI(title="Goings OS GHL Production Listener")

ROOT_DIR = os.environ.get(
    "GOINGS_OS_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)
DATA_VAULT = os.path.join(ROOT_DIR, "data", "goings_os_vault.db")
DB_PATH = DATA_VAULT if os.path.exists(DATA_VAULT) else os.path.join(ROOT_DIR, "goings_os_vault.db")


@app.post("/webhook/ghl/transaction")
async def receive_ghl_webhook(request: Request):
    payload = await request.json()

    # Extract data from the GHL webhook object (70/30 programmatic split governance)
    gross_amount = float(payload.get("amount", payload.get("transaction_amount", 0.0)))
    net_allocation = round(gross_amount * 0.30, 2)
    source = "GHL_PRODUCTION_WEBHOOK"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    client_name = str(payload.get("client_name", payload.get("contact_name", "GHL_PRODUCTION_CLIENT")))
    txn_id = str(payload.get("transaction_id", f"TXN-{int(time.time())}"))

    # Write to local vault with WAL concurrency
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("PRAGMA busy_timeout = 30000;")
    c.execute("""
        CREATE TABLE IF NOT EXISTS owners_draw_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            client_name TEXT,
            form_name TEXT,
            transaction_id TEXT,
            allocated_amount REAL,
            allocation_description TEXT,
            source_origin TEXT,
            gross_amount REAL DEFAULT 0.0,
            net_allocation REAL DEFAULT 0.0,
            tracking_status TEXT DEFAULT 'VERIFIED_PRODUCTION'
        )
    """)
    c.execute("""
        INSERT INTO owners_draw_allocations (
            timestamp, client_name, form_name, transaction_id,
            allocated_amount, allocation_description, source_origin,
            gross_amount, net_allocation, tracking_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        client_name,
        "GHL Production Webhook",
        txn_id,
        net_allocation,
        f"GHL Production Ingress: Gross ${gross_amount:.2f}; Owners Draw (30%): ${net_allocation:.2f}",
        source,
        gross_amount,
        net_allocation,
        "VERIFIED_PRODUCTION",
    ))
    conn.commit()
    conn.close()

    return {
        "status": "SUCCESS",
        "message": "Transaction routed to vault",
        "gross_amount": gross_amount,
        "owners_draw_allocation": net_allocation,
    }
