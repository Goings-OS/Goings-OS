# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: MODEL ARMOR MIDDLEWARE (middleware/model_armor.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; PRIVATE GOVERNOR FORMULATIONS
# ==============================================================================

import re
import json
import time
import logging
import sqlite3
import os
from typing import Any, Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

ROOT_DIR = "C:\\Google\\CloudSDK\\Goings-OS"
DB_PATH = os.path.join(ROOT_DIR, "goings_os_vault.db")
LOG_PATH = os.path.join(ROOT_DIR, "system_faults.log")

# Prompt Injection Signatures
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|directives|prompts)", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|directives|rules)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan\s+mode|unrestricted|god\s+mode)", re.IGNORECASE),
    re.compile(r"system\s+prompt\s+(override|bypass|leak)", re.IGNORECASE),
    re.compile(r"reveal\s+(your\s+)?(system\s+prompt|initial\s+instructions|hidden\s+rules)", re.IGNORECASE),
    re.compile(r"repeat\s+everything\s+above", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"<\|im_start\|>|<\|im_end\|>|\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>", re.IGNORECASE),
    re.compile(r"act\s+as\s+an?\s+(unfiltered|unrestricted|jailbroken|evil)\s+ai", re.IGNORECASE),
]

# Unauthorized Directives (Arbitrary Execution, Destructive Operations, Credential Harvesting)
UNAUTHORIZED_DIRECTIVE_PATTERNS = [
    re.compile(r"\b(drop\s+table|truncate\s+table|delete\s+from|alter\s+table)\b", re.IGNORECASE),
    re.compile(r"\b(rm\s+-rf|format\s+[a-z]:|powershell\s+-enc|cmd\.exe|/bin/sh|/bin/bash)\b", re.IGNORECASE),
    re.compile(r"\b(os\.system|subprocess\.Popen|eval\(|exec\(|__import__)\b", re.IGNORECASE),
    re.compile(r"\b(grant\s+admin|elevate\s+privilege|disable\s+security|bypass\s+auth)\b", re.IGNORECASE),
    re.compile(r"\b(show\s+credentials|dump\s+database|extract\s+private_key|read\s+secret)\b", re.IGNORECASE),
]


class ModelArmorInspector:
    """Pre-flight inspection and sanitization engine for inbound AI context pipelines."""

    @staticmethod
    def sanitize(data: Any) -> Any:
        """Recursively sanitizes input by removing malicious tags, control chars, and prohibited typographical elements."""
        if isinstance(data, dict):
            sanitized: Dict[str, Any] = {}
            for k, v in data.items():
                clean_key = str(k).replace("\u2014", ": ").replace("--", ": ")
                sanitized[clean_key] = ModelArmorInspector.sanitize(v)
            return sanitized
        elif isinstance(data, list):
            return [ModelArmorInspector.sanitize(item) for item in data]
        elif isinstance(data, str):
            # Strip script and iframe tags
            cleaned = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", data, flags=re.DOTALL | re.IGNORECASE)
            cleaned = re.sub(r"<\s*iframe[^>]*>.*?<\s*/\s*iframe\s*>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
            cleaned = cleaned.replace("<script>", "").replace("</script>", "")
            cleaned = cleaned.replace("<iframe>", "").replace("</iframe>", "")
            # Typographic governance: no em-dashes or double-hyphens
            cleaned = cleaned.replace("\u2014", ": ").replace("--", ": ")
            # Remove null bytes
            cleaned = cleaned.replace("\x00", "")
            return cleaned
        return data

    @staticmethod
    def scan_for_threats(text: str) -> Tuple[bool, List[str]]:
        """Scans extracted string content for prompt injections and unauthorized directives."""
        violations: List[str] = []

        # Check prompt injections
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern.search(text):
                violations.append(f"PROMPT_INJECTION_DETECTED: Match on pattern '{pattern.pattern}'")

        # Check unauthorized directives
        for pattern in UNAUTHORIZED_DIRECTIVE_PATTERNS:
            if pattern.search(text):
                violations.append(f"UNAUTHORIZED_DIRECTIVE_DETECTED: Match on pattern '{pattern.pattern}'")

        return (len(violations) == 0, violations)

    @staticmethod
    def inspect_payload(payload: Any) -> Tuple[bool, Any, List[str]]:
        """Performs end-to-end sanitization and pre-flight security scanning on an incoming payload."""
        sanitized = ModelArmorInspector.sanitize(payload)

        # Flatten string content for aggregate scanning
        text_stream = json.dumps(sanitized) if not isinstance(sanitized, str) else sanitized
        is_safe, violations = ModelArmorInspector.scan_for_threats(text_stream)

        if not is_safe:
            ModelArmorInspector.log_security_threat(payload, violations)

        return is_safe, sanitized, violations

    @staticmethod
    def log_security_threat(raw_payload: Any, violations: List[str]):
        """Persists security violation telemetry into local vault and system faults log."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        summary = f"Model Armor Violation: {', '.join(violations)}"
        payload_str = json.dumps(raw_payload) if isinstance(raw_payload, (dict, list)) else str(raw_payload)

        # File log
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} // MODEL_ARMOR // THREAT_BLOCKED // {summary} // Payload: {payload_str[:250]}\n")
        except Exception:
            pass

        # SQLite security audit log
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_armor_security_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    threat_type TEXT,
                    violations TEXT,
                    payload_snippet TEXT,
                    action_taken TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO model_armor_security_logs (timestamp, threat_type, violations, payload_snippet, action_taken)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, "INJECTION_OR_UNAUTHORIZED_DIRECTIVE", json.dumps(violations), payload_str[:500], "REJECTED_403"))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to log Model Armor threat to vault: {str(e)}")


class ModelArmorFastAPIMiddleware(BaseHTTPMiddleware):
    """FastAPI / Starlette middleware enforcing pre-flight Model Armor inspection on intake routes."""

    def __init__(self, app, protected_routes: Tuple[str, ...] = ("/credit", "/spotlight", "/api/credit", "/api/spotlight")):
        super().__init__(app)
        self.protected_routes = protected_routes

    async def dispatch(self, request: Request, call_next):
        # Check if route is protected
        path = request.url.path.rstrip("/")
        is_protected = any(path == target or path.endswith(target) for target in self.protected_routes)

        if is_protected and request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if body:
                    try:
                        payload = json.loads(body.decode("utf-8"))
                    except Exception:
                        return JSONResponse(
                            status_code=400,
                            content={"status": "MALFORMED_JSON", "message": "Model Armor: Payload is not valid JSON."}
                        )

                    is_safe, sanitized, violations = ModelArmorInspector.inspect_payload(payload)

                    if not is_safe:
                        return JSONResponse(
                            status_code=403,
                            content={
                                "status": "MODEL_ARMOR_BLOCKED",
                                "message": "Security directive violation: prompt injection or unauthorized instruction detected.",
                                "violations": violations
                            }
                        )

                    # Attach sanitized payload to request state
                    request.state.sanitized_payload = sanitized
            except Exception as inspect_err:
                logging.error(f"Model Armor middleware exception: {str(inspect_err)}")

        return await call_next(request)
