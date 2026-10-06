# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: INGRESS GATEWAY SERVICE (ingress_gateway.py)
# COMPLIANCE: ZERO DASHES; PRIVATE GOVERNOR FORMULATIONS
# ==============================================================================

import os
import sys
import time
import json
import logging
import sqlite3
import hmac
import hashlib
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from a2wsgi import ASGIMiddleware
from waitress import serve

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

app = FastAPI(title="Private Ingress Gateway", version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

ROOT_DIR = os.environ.get("GOINGS_OS_ROOT", os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "goings_os_vault.db")

logging.basicConfig(level=logging.INFO, format="%(asctime)s UTC // PRIVATE_INGRESS_GATEWAY // %(levelname)s // %(message)s")

def query_vault_conglomerate_entities(entity_filter: str = None) -> Dict[str, Any]:
    entities_canonical = ["Keep It Goings LLC", "Tanita Brinkley Enterprises LLC", "Luxury Affairs Event Center LLC", "Choice Inc", "Luxury Decor & Rentals LLC", "Norfolk Takeover Cruise LLC"]
    results = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "vault_path": DB_PATH, "conglomerate_entities": []}

    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("PRAGMA busy_timeout = 30000;")
        cursor.execute("PRAGMA journal_mode=WAL;")

        cursor.execute("CREATE TABLE IF NOT EXISTS entity_filings (filing_id INTEGER PRIMARY KEY AUTOINCREMENT, entity_name TEXT NOT NULL, jurisdiction TEXT NOT NULL, filing_type TEXT NOT NULL, state_registration_id TEXT, statutory_due_date TEXT, filing_fee_cents INTEGER DEFAULT 0, status TEXT NOT NULL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS brands (brand_id INTEGER PRIMARY KEY AUTOINCREMENT, brand_name TEXT NOT NULL, domain TEXT, primary_pillar TEXT, compliance_ruleset TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS entity_document_archive (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_name TEXT NOT NULL, document_type TEXT, file_name TEXT, sha256_checksum TEXT, drive_folder_path TEXT, drive_file_id TEXT)")

        cursor.execute("SELECT COUNT(*) FROM entity_filings")
        if cursor.fetchone()[0] == 0:
            seed = [("Keep It Goings LLC", "VA_SCC", "ANNUAL_REPORT", "SCC-1001", "2026-12-31", 5000, "ACTIVE_GOOD_STANDING"), ("Tanita Brinkley Enterprises LLC", "VA_SCC", "ANNUAL_REPORT", "SCC-1002", "2026-12-31", 5000, "ACTIVE_GOOD_STANDING"), ("Luxury Affairs Event Center LLC", "VA_SCC", "ANNUAL_REPORT", "SCC-1003", "2026-12-31", 5000, "ACTIVE_GOOD_STANDING"), ("Choice Inc", "VA_SCC", "CORPORATE_REGISTRATION", "SCC-1004", "2026-12-31", 2500, "ACTIVE_GOOD_STANDING"), ("Luxury Decor & Rentals LLC", "VA_SCC", "ANNUAL_REPORT", "SCC-1005", "2026-12-31", 5000, "ACTIVE_GOOD_STANDING"), ("Norfolk Takeover Cruise LLC", "VA_SCC", "ANNUAL_REPORT", "SCC-1006", "2026-12-31", 5000, "ACTIVE_GOOD_STANDING")]
            cursor.executemany("INSERT INTO entity_filings (entity_name, jurisdiction, filing_type, state_registration_id, statutory_due_date, filing_fee_cents, status) VALUES (?, ?, ?, ?, ?, ?, ?)", seed)
            conn.commit()

        cursor.execute("SELECT * FROM entity_filings")
        filings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        for entity in entities_canonical:
            if entity_filter and entity_filter.lower() not in entity.lower(): continue
            entity_filings = [f for f in filings if entity.lower() in f.get("entity_name", "").lower()]
            results["conglomerate_entities"].append({"entity_name": entity, "status": "ACTIVE_GOOD_STANDING", "filings_count": len(entity_filings), "filings": entity_filings, "archived_documents": []})
            
        results["total_entities"] = len(results["conglomerate_entities"])
    except Exception as err:
        results["error"] = str(err)
        for entity in entities_canonical:
            results["conglomerate_entities"].append({"entity_name": entity, "status": "REGISTERED_CANONICAL", "filings": []})
    return results

@app.get("/mcp")
async def mcp_get_endpoint(request: Request): return JSONResponse(status_code=200, content={"status": "active", "mcp_version": "2024-11-05", "service": "goings-os-mcp"})

@app.post("/mcp")
async def mcp_post_endpoint(request: Request):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})
    req_id = body.get("id")

    if method == "tools/call":
        call_result = query_vault_conglomerate_entities(entity_filter=params.get("arguments", {}).get("entity_name"))
        return JSONResponse(status_code=200, content={"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(call_result)}], "isError": False}})
    
    if method == "tools/list":
        return JSONResponse(status_code=200, content={"jsonrpc": "2.0", "id": req_id, "result": {"tools": [{"name": "get_conglomerate_status", "description": "Query live conglomerate records.", "inputSchema": {"type": "object", "properties": {"entity_name": {"type": "string"}}}}]}})
    
    return JSONResponse(status_code=200, content={"jsonrpc": "2.0", "id": req_id, "result": {}})

wsgi_app = ASGIMiddleware(app)

if __name__ == "__main__":
    serve(wsgi_app, host="0.0.0.0", port=8080, threads=8)
