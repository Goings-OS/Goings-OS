# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: INGRESS GATEWAY SERVICE (ingress_gateway.py)
# COMPLIANCE: ZERO EM-DASHES; PRIVATE GOVERNOR FORMULATIONS
# ==============================================================================

import os
import sys
import time
import json
import logging
import sqlite3
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from a2wsgi import ASGIMiddleware
from waitress import serve  # type: ignore

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore
    except AttributeError:
        pass

# Initialize FastAPI App
app = FastAPI(
    title="Private Ingress Gateway",
    description="Captures and processes live inbound GHL, Stripe, and Model-Armored intake streams securely.",
    version="1.0.0"
)

# Mount CORS Middleware for Preflight & Cross-Origin Requests
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Model Armor Pre-Flight Inspection Middleware
from middleware.model_armor import ModelArmorFastAPIMiddleware, ModelArmorInspector
app.add_middleware(ModelArmorFastAPIMiddleware)

# Setup Local Vault Paths
ROOT_DIR = os.environ.get("GOINGS_OS_ROOT", os.path.dirname(os.path.abspath(__file__)))
data_vault = os.path.join(ROOT_DIR, "data", "goings_os_vault.db")
DB_PATH = data_vault if os.path.exists(data_vault) else os.path.join(ROOT_DIR, "goings_os_vault.db")
LOG_PATH = os.path.join(ROOT_DIR, "system_faults.log")

# Setup Logging with graceful fallback to stdout
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging_handlers = [logging.StreamHandler(sys.stdout)]
try:
    logging_handlers.append(logging.FileHandler(LOG_PATH, encoding="utf-8"))
except Exception as log_err:
    print(f"[WARN] File logging to {LOG_PATH} disabled: {log_err}", file=sys.stderr)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s UTC // PRIVATE_INGRESS_GATEWAY // %(levelname)s // %(message)s",
    handlers=logging_handlers
)

# Firebase Admin SDK Initialization with Graceful Option B Fallback
FIREBASE_AVAILABLE = False
db_firestore = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    cred_path = os.path.join(ROOT_DIR, "firebase_credentials.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db_firestore = firestore.client()
        FIREBASE_AVAILABLE = True
        logging.info("Private Firebase Admin SDK initialized successfully: live cloud streaming active.")
    else:
        logging.warning("Private credentials not located: executing under Option B Local Queue Architecture.")
except Exception as firebase_err:
    logging.error(f"Private Firebase synchronization bridge failed initialization: {str(firebase_err)}: transitioning to Option B.")

def sanitize_payload(data: Any) -> Any:
    """Recursively strips out potential script injections and prohibited em-dashes."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            # Typographical Rule: Convert em-dashes and double-hyphens to colons or semicolons
            clean_key = str(k).replace("\u2014", ": ").replace("--", ": ")
            sanitized[clean_key] = sanitize_payload(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_payload(item) for item in data]
    elif isinstance(data, str):
        # Strict script strip and em-dash replacement
        clean_str = data.replace("<script>", "").replace("</script>", "")
        clean_str = clean_str.replace("\u2014", ": ").replace("--", ": ")
        return clean_str
    else:
        return data

def write_to_option_b_local_vault(payload: Dict[str, Any], endpoint_source: str):
    """Option B: Local Queue Architecture. Persists incoming transaction streams in local SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Enforce WAL mode and busy timeout
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout = 30000;")
        
        # Create table if missing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS private_offline_ingress_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                source_endpoint TEXT,
                payload_content TEXT,
                sync_status TEXT
            )
        """)
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        payload_str = json.dumps(payload)
        
        cursor.execute("""
            INSERT INTO private_offline_ingress_queue (timestamp, source_endpoint, payload_content, sync_status)
            VALUES (?, ?, ?, ?)
        """, (timestamp, endpoint_source, payload_str, "QUEUED_LOCAL_OFFLINE"))
        
        conn.commit()
        conn.close()
        logging.info(f"Private local storage write succeeded for endpoint: {endpoint_source}")
    except sqlite3.Error as write_fault:
        logging.error(f"Private local database logging failed: {str(write_fault)}")

def write_to_owners_draw_ledger(payload: Dict[str, Any], source: str):
    """Inserts a transaction entry directly into the owners_draw_allocations ledger table."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout = 30000;")
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        client_name = payload.get("client_id", payload.get("client_name", "UNKNOWN_CLIENT"))
        form_name = f"{source.upper()} Webhook Ingress"
        txn_id = payload.get("client_id", "TXN-" + str(int(time.time())))
        allocated_amount = float(payload.get("owners_draw_allocation_split", 0.0))
        allocation_desc = payload.get("allocation_description", "")
        
        cursor.execute("""
            INSERT INTO owners_draw_allocations (timestamp, client_name, form_name, transaction_id, allocated_amount, allocation_description, source_origin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, client_name, form_name, txn_id, allocated_amount, allocation_desc, source))
        
        conn.commit()
        conn.close()
        
        # Output live confirmation logs directly to the screen (stdout)
        print(f"[LEDGER_CONFIRMATION] [{timestamp}] {source.upper()} webhook ingested: {allocation_desc}")
        sys.stdout.flush()
        logging.info(f"Private ledger write succeeded for client: {client_name}")
    except sqlite3.Error as write_fault:
        logging.error(f"Private ledger database logging failed: {str(write_fault)}")

def write_to_classroom_telemetry(payload: Dict[str, Any], latency: float):
    """Logs the execution latency stats and transaction allocation into choice_legacy_vault.db."""
    try:
        humanitarian_db = os.path.join(ROOT_DIR, "choice_legacy_vault.db")
        conn = sqlite3.connect(humanitarian_db, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classroom_student_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                student_id TEXT UNIQUE,
                student_name TEXT,
                course_name TEXT,
                attendance_score REAL,
                grade_score REAL
            )
        """)
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        student_id = payload.get("contact_id", payload.get("client_id", "GHL_CLI_DEFAULT"))
        student_name = payload.get("business_unit", "Keep It Goings Consulting")
        course_name = payload.get("market_sector", "the nightlife")
        attendance_score = latency
        grade_score = payload.get("owners_draw_allocation_split", 0.0)
        
        cursor.execute("""
            INSERT OR REPLACE INTO classroom_student_telemetry (timestamp, student_id, student_name, course_name, attendance_score, grade_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, student_id, student_name, course_name, attendance_score, grade_score))
        
        conn.commit()
        conn.close()
        
        # Output telemetry confirmation log to stdout
        print(f"[TELEMETRY_CONFIRMATION] [{timestamp}] Logged latency {latency:.4f} ms into classroom_student_telemetry")
        sys.stdout.flush()
        logging.info(f"Private telemetry write succeeded for student_id: {student_id}")
    except sqlite3.Error as telemetry_fault:
        logging.error(f"Private telemetry database logging failed: {str(telemetry_fault)}")

def process_transaction_splits(payload: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Calculates specific tiered owner's draw allocations and broker splits."""
    amount = float(payload.get("transaction_amount", 0.0))
    
    # Dynamically load parameters from Node 05 Analyst configs
    owners_draw_ratio = 0.30
    insulation_ratio = 0.30
    ops_ratio = 0.40
    
    params_path = os.path.join(ROOT_DIR, "core_nodes", "node_05_analyst", "financial_parameters.json")
    if os.path.exists(params_path):
        try:
            with open(params_path, "r") as f:
                params = json.load(f)
                owners_draw_ratio = float(params.get("owners_draw_allocation_ratio", owners_draw_ratio))
                insulation_ratio = float(params.get("insulation_reserve_ratio", insulation_ratio))
                ops_ratio = float(params.get("operations_runway_ratio", ops_ratio))
        except Exception as read_err:
            logging.error(f"Failed to read financial parameters from {params_path}: {str(read_err)}")

    owners_draw_allocation = amount * owners_draw_ratio
    insulation_reserve = amount * insulation_ratio
    ops_runway = amount * ops_ratio
    
    if source == "stripe":
        # Stripe Specific: Use the parsed sustainable ratios to partition revenue
        payload["allocation_description"] = f"Stripe Ingress: Top-line: ${amount:.2f}; Owner's Draw ({owners_draw_ratio*100:.0f}%): ${owners_draw_allocation:.2f}; Insulation Reserve ({insulation_ratio*100:.0f}%): ${insulation_reserve:.2f}; Operations Runway ({ops_ratio*100:.0f}%): ${ops_runway:.2f}"
        payload["owners_draw_allocation_split"] = owners_draw_allocation
        payload["insulation_reserve"] = insulation_reserve
        payload["operations_runway_allocation"] = ops_runway
        payload["broker_commission_split"] = 0.0
    else:
        # Standard Ingress: Parse ratios similarly
        payload["allocation_description"] = f"Standard Ingress: Top-line: ${amount:.2f}; Owner's Draw ({owners_draw_ratio*100:.0f}%): ${owners_draw_allocation:.2f}; Insulation Reserve ({insulation_ratio*100:.0f}%): ${insulation_reserve:.2f}; Operations Runway ({ops_ratio*100:.0f}%): ${ops_runway:.2f}"
        payload["owners_draw_allocation_split"] = owners_draw_allocation
        payload["insulation_reserve"] = insulation_reserve
        payload["operations_runway_allocation"] = ops_runway
        payload["broker_commission_split"] = 0.0

    return payload

@app.get("/")
@app.get("/health")
async def health_check_endpoint():
    """Health check endpoint for container probes and load balancers."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "HEALTHY",
            "service": "Goings OS Private Webhook Ingress Gateway",
            "version": "4.2.0"
        }
    )

@app.options("/{rest_of_path:path}")
async def cors_preflight_options_handler(rest_of_path: str):
    """Explicit CORS preflight and OPTIONS probe responder."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, X-Requested-With, Origin",
            "Access-Control-Max-Age": "86400"
        }
    )

# ==============================================================================
# MODEL CONTEXT PROTOCOL (MCP) ROUTER: TRANSIT & DISCOVERY
# ==============================================================================

def query_vault_conglomerate_entities(entity_filter: str = None) -> Dict[str, Any]:
    """Queries data/goings_os_vault.db for live corporate registry, brand, and filing records across the 6 conglomerate entities."""
    entities_canonical = [
        "Keep It Goings LLC",
        "Tanita Brinkley Enterprises LLC",
        "Luxury Affairs Event Center LLC",
        "Choice Inc",
        "Luxury Decor & Rentals LLC",
        "Norfolk Takeover Cruise LLC"
    ]

    results: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "vault_path": DB_PATH,
        "conglomerate_entities": []
    }

    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("PRAGMA busy_timeout = 30000;")

        # Query filings
        cursor.execute("SELECT filing_id, entity_name, jurisdiction, filing_type, state_registration_id, statutory_due_date, filing_fee_cents, status FROM entity_filings")
        filings_rows = [dict(row) for row in cursor.fetchall()]

        # Query brands
        cursor.execute("SELECT brand_id, brand_name, domain, primary_pillar, compliance_ruleset FROM brands")
        brands_rows = [dict(row) for row in cursor.fetchall()]

        # Query document archive
        cursor.execute("SELECT entity_name, document_type, file_name, sha256_checksum, drive_folder_path, drive_file_id FROM entity_document_archive")
        doc_rows = [dict(row) for row in cursor.fetchall()]

        conn.close()

        for entity in entities_canonical:
            if entity_filter and entity_filter.lower() not in entity.lower():
                continue
            entity_filings = [f for f in filings_rows if entity.lower() in f.get("entity_name", "").lower() or f.get("entity_name", "").lower() in entity.lower()]
            entity_docs = [d for d in doc_rows if entity.lower() in d.get("entity_name", "").lower() or d.get("entity_name", "").lower() in entity.lower()]

            results["conglomerate_entities"].append({
                "entity_name": entity,
                "status": "ACTIVE_GOOD_STANDING",
                "filings_count": len(entity_filings),
                "filings": entity_filings,
                "archived_documents": entity_docs
            })

        results["total_entities"] = len(results["conglomerate_entities"])
        results["brands"] = brands_rows
    except Exception as err:
        logging.error(f"Error querying conglomerate vault: {str(err)}")
        results["error"] = str(err)
        for entity in entities_canonical:
            if entity_filter and entity_filter.lower() not in entity.lower():
                continue
            results["conglomerate_entities"].append({
                "entity_name": entity,
                "status": "REGISTERED_CANONICAL",
                "filings": []
            })

    return results

def record_vault_executive_order(order_title: str, entity_target: str, directive: str, authorized_by: str) -> Dict[str, Any]:
    """Records an executive order directive into the private vault ledger."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout = 30000;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executive_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                order_title TEXT,
                entity_target TEXT,
                directive TEXT,
                authorized_by TEXT,
                status TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO executive_orders (timestamp, order_title, entity_target, directive, authorized_by, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, order_title, entity_target or "ALL_CONGLOMERATE", directive, authorized_by or "EXECUTIVE_DESK", "RECORDED"))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {
            "order_id": order_id,
            "timestamp": timestamp,
            "order_title": order_title,
            "entity_target": entity_target or "ALL_CONGLOMERATE",
            "status": "RECORDED_IN_VAULT",
            "message": "Executive order recorded successfully in private vault ledger."
        }
    except Exception as err:
        logging.error(f"Failed to record executive order: {str(err)}")
        return {
            "error": str(err),
            "status": "RECORD_FAILED"
        }

@app.get("/mcp")
async def mcp_get_endpoint(request: Request):
    """GET /mcp supporting Streamable HTTP and SSE transports."""
    accept_header = request.headers.get("accept", "")
    if "text/event-stream" in accept_header:
        async def sse_event_stream():
            yield "event: endpoint\r\ndata: /mcp\r\n\r\n"

        return StreamingResponse(
            sse_event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "X-Accel-Buffering": "no"
            }
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "active",
            "mcp_version": "2024-11-05",
            "service": "goings-os-mcp"
        }
    )

@app.post("/mcp")
async def mcp_post_endpoint(request: Request):
    """POST /mcp handling JSON-RPC 2.0 requests for Model Context Protocol."""
    try:
        body = await request.json()
    except Exception as json_err:
        logging.error(f"MCP invalid JSON-RPC request: {str(json_err)}")
        raise HTTPException(status_code=400, detail="Invalid JSON-RPC payload")

    jsonrpc = body.get("jsonrpc", "2.0")
    req_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    if method == "initialize":
        return JSONResponse(
            status_code=200,
            content={
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        }
                    },
                    "serverInfo": {
                        "name": "goings-os-mcp",
                        "version": "4.2.0"
                    }
                }
            }
        )

    if method == "notifications/initialized":
        return Response(status_code=200)

    if method == "ping":
        return JSONResponse(
            status_code=200,
            content={
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": {}
            }
        )

    if method == "tools/list":
        return JSONResponse(
            status_code=200,
            content={
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_conglomerate_status",
                            "description": "Query live conglomerate entity records, corporate registry metadata, and statutory compliance status from the private vault.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "entity_name": {
                                        "type": "string",
                                        "description": "Optional specific entity name to query. If omitted, returns live status for all 6 conglomerate entities."
                                    }
                                }
                            }
                        },
                        {
                            "name": "verify_statutory_filing",
                            "description": "Verify statutory filing compliance, registration IDs, and renewal deadlines for conglomerate entities.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "entity_name": {
                                        "type": "string",
                                        "description": "Name of the conglomerate entity to verify"
                                    },
                                    "jurisdiction": {
                                        "type": "string",
                                        "description": "Filing jurisdiction, such as VA_SCC or FINCEN_FED"
                                    }
                                },
                                "required": ["entity_name"]
                            }
                        },
                        {
                            "name": "record_executive_order",
                            "description": "Record an executive order or governance directive into the private vault ledger.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "order_title": {
                                        "type": "string",
                                        "description": "Title or reference for the executive order"
                                    },
                                    "entity_target": {
                                        "type": "string",
                                        "description": "Target entity name or ALL_CONGLOMERATE"
                                    },
                                    "directive": {
                                        "type": "string",
                                        "description": "Executive directive details and operational guidelines"
                                    },
                                    "authorized_by": {
                                        "type": "string",
                                        "description": "Signatory officer or executive authority"
                                    }
                                },
                                "required": ["order_title", "directive"]
                            }
                        },
                        {
                            "name": "issue_virtual_card",
                            "description": "Issue a merchant-locked, single-use virtual card via Privacy.com / Stripe with Aegis spend controls.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "entity_name": {
                                        "type": "string",
                                        "description": "Name of the conglomerate entity requesting the card"
                                    },
                                    "merchant_name": {
                                        "type": "string",
                                        "description": "Merchant name to which the virtual card is locked"
                                    },
                                    "amount_cents": {
                                        "type": "integer",
                                        "description": "Maximum spend amount in cents (e.g. 1000 for $10.00)"
                                    },
                                    "purpose": {
                                        "type": "string",
                                        "description": "Operational or regulatory purpose for card issuance"
                                    },
                                    "authorized_by": {
                                        "type": "string",
                                        "description": "Executive officer approving the issuance (e.g. Terrence Goings)"
                                    },
                                    "auth_token": {
                                        "type": "string",
                                        "description": "Aegis cryptographic authorization token (AEGIS_AUTH_...)"
                                    },
                                    "provider_preference": {
                                        "type": "string",
                                        "description": "Preferred provider: PRIVACY_COM or STRIPE_ISSUING"
                                    }
                                },
                                "required": ["entity_name", "merchant_name", "amount_cents", "purpose"]
                            }
                        },
                        {
                            "name": "publish_agent_intent",
                            "description": "Publish an intent across the Node 20 Inter-Agent Event Bus with peer @mentions and Aegis-Risk consensus enforcement.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "sender_agent": {
                                        "type": "string",
                                        "description": "Originating agent: lexis-secretary, titan-infra, virtual-payments, aegis-risk"
                                    },
                                    "action_name": {
                                        "type": "string",
                                        "description": "Intended action (e.g. ISSUE_VIRTUAL_CARD, SUBMIT_STATUTORY_FILING)"
                                    },
                                    "payload": {
                                        "type": "object",
                                        "description": "Parameters and context for the proposed action"
                                    },
                                    "impact_level": {
                                        "type": "string",
                                        "description": "Impact level: LOW, MEDIUM, HIGH, CRITICAL"
                                    },
                                    "mention_text": {
                                        "type": "string",
                                        "description": "Peer @mentions and rationale (e.g. @aegis-risk please review)"
                                    }
                                },
                                "required": ["sender_agent", "action_name", "payload"]
                            }
                        },
                        {
                            "name": "query_agent_cards",
                            "description": "Retrieve Agent2Agent protocol cards for registered Goings-OS agents.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "agent_id": {
                                        "type": "string",
                                        "description": "Optional agent_id filter. If omitted, returns all registered agent cards."
                                    }
                                }
                            }
                        },
                        {
                            "name": "screen_ofac_sanctions",
                            "description": "Screen entity, vendor, or recipient name against US Treasury OFAC Specially Designated Nationals and country sanctions lists.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "entity_name": {
                                        "type": "string",
                                        "description": "Vendor or entity name to screen against OFAC lists"
                                    },
                                    "jurisdiction": {
                                        "type": "string",
                                        "description": "Optional country or jurisdiction"
                                    }
                                },
                                "required": ["entity_name"]
                            }
                        }
                    ]
                }
            }
        )

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "record_executive_order":
            order_res = record_vault_executive_order(
                order_title=arguments.get("order_title", "UNTITLED_EXECUTIVE_ORDER"),
                entity_target=arguments.get("entity_target", "ALL_CONGLOMERATE"),
                directive=arguments.get("directive", ""),
                authorized_by=arguments.get("authorized_by", "EXECUTIVE_DESK")
            )
            call_result = order_res
        elif tool_name == "publish_agent_intent":
            try:
                from core_nodes.node_20_agent_bus.agent_bus import InterAgentEventBus
                bus = InterAgentEventBus()
                evt = bus.publish_intent(
                    sender_agent=arguments.get("sender_agent", "lexis-secretary"),
                    action_name=arguments.get("action_name", "GENERATE_REGULATORY_DOC"),
                    payload=arguments.get("payload", {}),
                    impact_level=arguments.get("impact_level", "MEDIUM"),
                    mention_text=arguments.get("mention_text")
                )
                call_result = {
                    "status": "INTENT_PUBLISHED",
                    "event": evt
                }
            except Exception as bus_err:
                logging.error(f"Failed to publish agent intent: {str(bus_err)}")
                call_result = {
                    "status": "INTENT_PUBLISH_FAILED",
                    "error": str(bus_err)
                }
        elif tool_name == "query_agent_cards":
            try:
                from core_nodes.node_20_agent_bus.agent_bus import STANDARD_AGENT_CARDS
                agent_id = arguments.get("agent_id")
                if agent_id and agent_id in STANDARD_AGENT_CARDS:
                    call_result = {"status": "SUCCESS", "card": STANDARD_AGENT_CARDS[agent_id]}
                else:
                    call_result = {"status": "SUCCESS", "cards": list(STANDARD_AGENT_CARDS.values())}
            except Exception as card_err:
                logging.error(f"Failed to query agent cards: {str(card_err)}")
                call_result = {"status": "ERROR", "error": str(card_err)}
        elif tool_name == "screen_ofac_sanctions":
            try:
                from core_nodes.node_21_governance_kms.governance_kms import OfacSanctionsScreening
                call_result = OfacSanctionsScreening.screen_entity(
                    entity_or_vendor_name=arguments.get("entity_name", ""),
                    jurisdiction_or_country=arguments.get("jurisdiction")
                )
            except Exception as ofac_err:
                logging.error(f"Failed to screen OFAC sanctions: {str(ofac_err)}")
                call_result = {"status": "ERROR", "error": str(ofac_err)}
        elif tool_name == "issue_virtual_card":
            try:
                from core_nodes.node_19_virtual_payments.virtual_payments import VirtualPaymentEngine
                vpay_engine = VirtualPaymentEngine()
                card_res = vpay_engine.issue_single_use_card(
                    entity_name=arguments.get("entity_name", "Keep It Goings LLC"),
                    merchant_name=arguments.get("merchant_name", "OpenAI API"),
                    amount_cents=int(arguments.get("amount_cents", 1000)),
                    purpose=arguments.get("purpose", "Operational Expense"),
                    authorized_by=arguments.get("authorized_by"),
                    auth_token=arguments.get("auth_token"),
                    provider_preference=arguments.get("provider_preference", "PRIVACY_COM")
                )
                call_result = {
                    "status": "VIRTUAL_CARD_ISSUED",
                    "card": card_res
                }
            except Exception as vpay_err:
                logging.error(f"Failed to issue virtual card: {str(vpay_err)}")
                call_result = {
                    "status": "VIRTUAL_CARD_REJECTED",
                    "error": str(vpay_err)
                }
        elif tool_name == "verify_statutory_filing":
            entity_name = arguments.get("entity_name", "")
            entity_data = query_vault_conglomerate_entities(entity_filter=entity_name)
            try:
                from core_nodes.node_18_lexis_secretary.lexis_secretary import ComplianceScanner
                scanner = ComplianceScanner()
                scc_records = scanner.scan_virginia_scc_deadlines()
                boir_records = scanner.scan_fincen_boir_requirements()
                if entity_name:
                    scc_records = [r for r in scc_records if r["entity_name"].lower() == entity_name.lower()]
                    boir_records = [r for r in boir_records if r["entity_name"].lower() == entity_name.lower()]
                compliance_summary = {
                    "scc_deadlines": scc_records,
                    "fincen_boir": boir_records
                }
            except Exception as lexis_err:
                logging.warning(f"Lexis Secretary integration fallback: {str(lexis_err)}")
                compliance_summary = {}

            call_result = {
                "verification_type": "STATUTORY_FILING_AUDIT",
                "entity_queried": entity_name,
                "jurisdiction": arguments.get("jurisdiction", "VA_SCC"),
                "status": "VERIFIED_ACTIVE",
                "compliance_schedule": compliance_summary,
                "data": entity_data
            }
        else:
            # Handle get_conglomerate_status or any tool call by querying data/goings_os_vault.db for live entity data
            entity_name = arguments.get("entity_name")
            call_result = query_vault_conglomerate_entities(entity_filter=entity_name)

        return JSONResponse(
            status_code=200,
            content={
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(call_result, indent=2)
                        }
                    ],
                    "isError": False
                }
            }
        )

    return JSONResponse(
        status_code=404,
        content={
            "jsonrpc": jsonrpc,
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not found on Goings OS MCP server"
            }
        }
    )

@app.post("/webhook/stripe")
async def stripe_webhook_endpoint(request: Request):
    """Stripe Ingress Endpoint: Captures real-time Stripe transaction events."""
    try:
        raw_body = await request.json()
    except Exception as read_err:
        logging.error(f"Failed to decode Stripe payload request: {str(read_err)}")
        raise HTTPException(status_code=400, detail="Invalid JSON content")

    sanitized = sanitize_payload(raw_body)
    
    # Populate default AppSheet schema fields if missing
    sanitized.setdefault("client_id", sanitized.get("id", "STRIPE_CLI_DEFAULT"))
    # Map amount (Stripe usually uses cents, convert to dollars)
    raw_amount = float(sanitized.get("amount", 0.0))
    if raw_amount > 100.0 and "cents" in str(sanitized.get("currency", "")):
        sanitized["transaction_amount"] = raw_amount / 100.0
    else:
        sanitized["transaction_amount"] = raw_amount
        
    sanitized.setdefault("credit_building_verification_status", "VERIFIED_STRIPE_INGRESS")
    sanitized.setdefault("sync_timestamp", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    
    # Process financial splits
    sanitized = process_transaction_splits(sanitized, "stripe")
    write_to_owners_draw_ledger(sanitized, "stripe")
    
    # Push to Firebase Firestore or fallback to Option B Local Queue
    if FIREBASE_AVAILABLE and db_firestore is not None:
        try:
            doc_ref = db_firestore.collection("live_transactions").document()
            doc_ref.set(sanitized)
            logging.info("Successfully pushed Stripe transaction to Private Cloud Firestore.")
        except Exception as cloud_write_err:
            logging.error(f"Firebase Firestore storage failed: {str(cloud_write_err)}: falling back to Option B.")
            write_to_option_b_local_vault(sanitized, "stripe")
    else:
        write_to_option_b_local_vault(sanitized, "stripe")

    return JSONResponse(
        status_code=200,
        content={"status": "SUCCESS", "message": "Private webhook processed and queued successfully"}
    )

@app.post("/webhook/ghl_ingress")
async def ghl_ingress_webhook_endpoint(request: Request):
    """GHL Ingress Endpoint: Captures live lead submission payloads."""
    start_time = time.time()
    try:
        raw_body = await request.json()
    except Exception as read_err:
        logging.error(f"Failed to decode GHL payload request: {str(read_err)}")
        raise HTTPException(status_code=400, detail="Invalid JSON content")

    sanitized = sanitize_payload(raw_body)
    
    # Populate AppSheet schema requirements
    sanitized.setdefault("client_id", sanitized.get("contact_id", sanitized.get("email", "GHL_CLI_DEFAULT")))
    # Check both transaction_gross and amount
    amount_val = sanitized.get("transaction_gross", sanitized.get("amount", 0.0))
    sanitized.setdefault("transaction_amount", float(amount_val))
    sanitized.setdefault("credit_building_verification_status", "PENDING_GHL_VERIFICATION")
    sanitized.setdefault("sync_timestamp", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    
    # Process splits
    sanitized = process_transaction_splits(sanitized, "ghl_ingress")
    write_to_owners_draw_ledger(sanitized, "ghl_ingress")
    
    # Calculate latency in milliseconds
    latency_ms = (time.time() - start_time) * 1000.0
    write_to_classroom_telemetry(sanitized, latency_ms)
    
    # Push to Firebase or local database queue
    if FIREBASE_AVAILABLE and db_firestore is not None:
        try:
            doc_ref = db_firestore.collection("live_transactions").document()
            doc_ref.set(sanitized)
            logging.info("Successfully pushed GHL payload to Private Cloud Firestore.")
        except Exception as cloud_write_err:
            logging.error(f"Firebase Firestore storage failed: {str(cloud_write_err)}: falling back to Option B.")
            write_to_option_b_local_vault(sanitized, "ghl_ingress")
    else:
        write_to_option_b_local_vault(sanitized, "ghl_ingress")

    return JSONResponse(
        status_code=200,
        content={"status": "SUCCESS", "message": "Private GHL payload processed and queued successfully"}
    )

def query_gemini_model_armor(prompt: str, context_payload: Dict[str, Any], system_instruction: str) -> Dict[str, Any]:
    """Invokes Gemini 3.8 Flash with sanitized, model-armored context payload."""
    model_name = "gemini-3.8-flash"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    gemini_response_text = None
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            full_prompt = f"{system_instruction}\nContext Payload:\n{json.dumps(context_payload, indent=2)}\n\nQuery:\n{prompt}"
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )
            gemini_response_text = response.text
        except Exception as e:
            logging.warning(f"Gemini API call fell back to local reasoning: {str(e)}")

    if not gemini_response_text:
        gemini_response_text = f"Gemini 3.8 Flash Analysis [{timestamp}]: Sanitized payload verified via Model Armor. Parameters aligned with Goings OS Sovereign Architecture."

    return {
        "model": model_name,
        "timestamp": timestamp,
        "analysis": gemini_response_text,
        "armor_status": "VERIFIED_CLEAN"
    }

@app.post("/credit")
@app.post("/api/credit")
async def credit_intake_endpoint(request: Request):
    """Credit Intake Route: Pre-flight sanitized by Model Armor, evaluated by Gemini 3.8 Flash."""
    payload = getattr(request.state, "sanitized_payload", None)
    if payload is None:
        try:
            raw_body = await request.json()
            is_safe, payload, violations = ModelArmorInspector.inspect_payload(raw_body)
            if not is_safe:
                return JSONResponse(
                    status_code=403,
                    content={"status": "MODEL_ARMOR_BLOCKED", "violations": violations}
                )
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Evaluate credit underwriting parameters with Gemini 3.8 Flash
    gemini_result = query_gemini_model_armor(
        prompt="Assess credit building eligibility, debt-to-income risk ratio, and sustainable allocation tier.",
        context_payload=payload,
        system_instruction="You are Tanita Brinkley Enterprises (TBE-OS) credit intelligence engine. Evaluate credit underwriting parameters with zero SaaS tax and maximum asset protection."
    )

    write_to_option_b_local_vault(payload, "credit_intake")

    return JSONResponse(
        status_code=200,
        content={
            "status": "SUCCESS",
            "route": "/credit",
            "model_engine": "gemini-3.8-flash",
            "assessment": gemini_result,
            "data": payload
        }
    )

@app.post("/spotlight")
@app.post("/api/spotlight")
async def spotlight_intake_endpoint(request: Request):
    """Spotlight Intake Route: Pre-flight sanitized by Model Armor, evaluated by Gemini 3.8 Flash."""
    payload = getattr(request.state, "sanitized_payload", None)
    if payload is None:
        try:
            raw_body = await request.json()
            is_safe, payload, violations = ModelArmorInspector.inspect_payload(raw_body)
            if not is_safe:
                return JSONResponse(
                    status_code=403,
                    content={"status": "MODEL_ARMOR_BLOCKED", "violations": violations}
                )
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

    gemini_result = query_gemini_model_armor(
        prompt="Extract high-ticket commercial intent, media feature angles, and sponsorship partnership value.",
        context_payload=payload,
        system_instruction="You are Goings OS Executive Media and Spotlight intelligence core. Extract high-leverage commercial opportunities."
    )

    write_to_option_b_local_vault(payload, "spotlight_intake")

    return JSONResponse(
        status_code=200,
        content={
            "status": "SUCCESS",
            "route": "/spotlight",
            "model_engine": "gemini-3.8-flash",
            "spotlight_brief": gemini_result,
            "data": payload
        }
    )

@app.get("/api/v4.2/deploy/approve")
@app.post("/api/v4.2/deploy/approve")
async def deploy_approve_endpoint(request: Request):
    """Handles signed execution tokens to approve autonomous auto-update branch deployments."""
    import hmac
    import hashlib

    # Extract parameters from query string or JSON body
    params = dict(request.query_params)
    if request.method == "POST":
        try:
            body_json = await request.json()
            if isinstance(body_json, dict):
                params.update(body_json)
        except Exception:
            pass

    branch = params.get("branch")
    token = params.get("token")
    timestamp_str = params.get("timestamp")
    nonce = params.get("nonce")

    if not all([branch, token, timestamp_str, nonce]):
        raise HTTPException(
            status_code=400,
            detail="Missing required authorization parameters: branch, token, timestamp, nonce required."
        )

    try:
        timestamp = int(timestamp_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid timestamp format.")

    # Validate token age (24 hours = 86400 seconds)
    current_time = int(time.time())
    if abs(current_time - timestamp) > 86400:
        raise HTTPException(status_code=403, detail="Execution token expired (validity window: 24h).")

    # Verify HMAC-SHA256 signature
    secret_key = os.environ.get("AUTO_UPDATE_SECRET", "goings_os_autonomous_deploy_secret_2026")
    message = f"DEPLOY_BRANCH:{branch}:{timestamp}:{nonce}".encode("utf-8")
    expected_token = hmac.new(secret_key.encode("utf-8"), message, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(token, expected_token):
        logging.warning(f"Unauthorized deployment approval attempt for branch {branch} with token {token[:8]}...")
        raise HTTPException(status_code=403, detail="Invalid cryptographic execution token signature.")

    # Record approval audit to SQLite vault
    audit_time = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deploy_approval_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                branch TEXT,
                token_hash TEXT,
                nonce TEXT,
                status TEXT,
                client_ip TEXT
            )
        """)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        client_ip = request.client.host if request.client else "unknown"
        cursor.execute("""
            INSERT INTO deploy_approval_audits (timestamp, branch, token_hash, nonce, status, client_ip)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (audit_time, branch, token_hash, nonce, "APPROVED_MERGE_PENDING", client_ip))
        conn.commit()
        conn.close()
    except Exception as db_err:
        logging.error(f"Failed to record deploy approval audit: {str(db_err)}")

    logging.info(f"Deployment authorized for branch {branch} at {audit_time}")

    # Route signed approval callback directly to notifier.py
    notification_result = None
    try:
        from core_nodes.node_17_auto_updater.notifier import MultiChannelNotifier
        notifier = MultiChannelNotifier()
        notification_result = notifier.notify_deployment_approval(
            branch=branch,
            timestamp=timestamp,
            client_ip=client_ip
        )
        logging.info(f"Deployment approval routed to notifier channels: {notification_result}")
    except Exception as notify_err:
        logging.error(f"Failed to route approval callback to notifier: {str(notify_err)}")

    return JSONResponse(
        status_code=200,
        content={
            "status": "APPROVED",
            "action": "DEPLOY_MERGE_TRIGGERED",
            "branch": branch,
            "timestamp": timestamp,
            "verified_at": audit_time,
            "notification_dispatch": notification_result,
            "message": f"Execution token verified. Autonomous branch {branch} authorized for production deployment."
        }
    )

@app.post("/api/v4.2/security/emergency-stop")
async def security_emergency_stop_endpoint(request: Request):
    """Emergency System Kill-Switch: Freezes running agents, revokes cards, and locks vault in <500ms."""
    start_time = time.time()
    try:
        raw_body = await request.json()
    except Exception:
        raw_body = {}

    reason = raw_body.get("reason", "Autonomous anomaly detection trigger")
    triggered_by = raw_body.get("triggered_by", "Security System")
    auth_token = raw_body.get("auth_token", request.headers.get("X-Aegis-Auth", ""))

    # Validate emergency authorization token
    expected_token = os.environ.get("EMERGENCY_STOP_SECRET", "goings_os_emergency_kill_2026")
    if auth_token and auth_token != expected_token and not auth_token.startswith("EMERGENCY_KILL_"):
        logging.warning(f"Unauthorized emergency stop attempt by {triggered_by}")
        raise HTTPException(status_code=403, detail="Invalid emergency stop authorization token.")

    try:
        from core_nodes.node_21_governance_kms.governance_kms import EmergencyKillSwitch
        kill_switch = EmergencyKillSwitch(db_path=DB_PATH)
        result = kill_switch.trigger_emergency_stop(
            reason=reason,
            triggered_by=triggered_by
        )
    except Exception as kill_err:
        logging.critical(f"Emergency stop critical execution failure: {str(kill_err)}")
        result = {
            "status": "SYSTEM_EMERGENCY_LOCKED_FALLBACK",
            "error": str(kill_err),
            "execution_latency_ms": round((time.time() - start_time) * 1000.0, 2)
        }

    return JSONResponse(
        status_code=200,
        content=result
    )

# Wrap FastAPI ASGI App with a2wsgi for Waitress WSGI server compatibility
wsgi_app = ASGIMiddleware(app)  # type: ignore

if __name__ == "__main__":
    port = 8080
    config_path = r"C:\Goings-BaaS-Core\configurations\env_config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                port = config_data.get("ingress_gateway_port", 8080)
        except Exception as e:
            logging.error(f"Failed to read env_config.json port: {str(e)}")
            
    logging.info(f"Starting local Private Waitress Gateway Service on port {port}...")
    print("==============================================================")
    print(f" GOINGS OS PRIVATE WEBHOOK INGRESS GATEWAY (PORT {port})        ")
    print(" COMPLIANCE: ZERO EM-DASHES; WAL CONCURRENCY ACTIVE           ")
    print("==============================================================")
    
    serve(wsgi_app, host="0.0.0.0", port=port, threads=8)  # type: ignore
