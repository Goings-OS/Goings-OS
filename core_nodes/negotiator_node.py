# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: AUTONOMOUS NEGOTIATOR & API INTEGRATION HUB
# COMPLIANCE: ZERO EM-DASHES; SECURE LOG SANITIZATION
# ==============================================================================

import os
import sys
import re
import time
import json

# Ensure parent directory is in sys.path when running this module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_nodes.memory_bank import PersistentMemoryBank

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class CredentialVault:
    """Provides secure in-memory storage for sensitive credentials and redacts them from logs."""

    def __init__(self):
        self._credentials = {}

    def store_credential(self, name: str, value: str):
        """Saves a sensitive credential value in the secure container."""
        if name:
            self._credentials[name.strip()] = value

    def get_credential(self, name: str) -> str:
        """Retrieves a stored credential value."""
        return self._credentials.get(name, "")

    def redact_data(self, data):
        """Recursively traverses dictionary structures, lists, and strings to sanitize secrets."""
        if isinstance(data, dict):
            redacted = {}
            for k, v in data.items():
                k_lower = k.lower()
                # Redact keys matching signature patterns
                if any(sig in k_lower for sig in ["key", "token", "secret", "password", "auth", "credential"]):
                    redacted[k] = "[REDACTED_SECURE_VALUE]"
                else:
                    redacted[k] = self.redact_data(v)
            return redacted
        elif isinstance(data, list):
            return [self.redact_data(item) for item in data]
        elif isinstance(data, str):
            redacted_str = data
            for name, val in self._credentials.items():
                if val and val in redacted_str:
                    redacted_str = redacted_str.replace(val, f"[REDACTED_{name.upper()}]")
            return redacted_str
        return data


class NegotiatorNode:
    """Serves as an MCP client facilitating interactions with enterprise endpoints."""

    def __init__(self, memory_bank: PersistentMemoryBank = None, vault: CredentialVault = None):
        self.memory_bank = memory_bank or PersistentMemoryBank()
        self.vault = vault or CredentialVault()
        self.tools = {}

    def register_tool(self, name: str, handler_callable, parameters_schema: dict = None):
        """Registers a dynamic API integration endpoint tool capability."""
        if not name:
            raise ValueError("Integration tool name cannot be empty")
        self.tools[name] = {
            "handler": handler_callable,
            "schema": parameters_schema or {}
        }
        print(f" -> Negotiator Node: Dynamic tool '{name}' successfully registered")

    def execute_negotiation(self, objective: str, tool_name: str, payload_data: dict) -> dict:
        """Constructs API payload, injects vault credentials, executes, and parses redacted response."""
        if tool_name not in self.tools:
            raise ValueError(f"Integration tool '{tool_name}' is not registered in the NegotiatorNode")

        tool = self.tools[tool_name]
        handler = tool["handler"]

        print(f"\n⚙️ [NEGOTIATOR] Initiating execution run for Objective: '{objective}'")

        # 1. Prepare payload by injecting credentials where necessary
        active_payload = payload_data.copy()
        
        # If payload expects credentials, resolve and inject them from the vault
        for k, v in active_payload.items():
            if isinstance(v, str) and v.startswith("vault://"):
                cred_name = v.replace("vault://", "")
                active_payload[k] = self.vault.get_credential(cred_name)

        # 2. Redact payload for logging purposes
        clean_log_payload = self.vault.redact_data(active_payload)
        print(f" -> Outbound payload prepared: {json.dumps(clean_log_payload)}")

        # 3. Invoke integration capability handler
        try:
            start_time = time.time()
            raw_response = handler(active_payload)
            elapsed_ms = (time.time() - start_time) * 1000.0

            # 4. Redact response before logging or syncing
            redacted_response = self.vault.redact_data(raw_response)
            print(f" -> Inbound response received in {elapsed_ms:.2f} milliseconds")
            print(f" -> Sanitized response parsed: {json.dumps(redacted_response)}")

            # 5. Log negotiation result into the local SQLite cache
            tenant = "Goings OS"
            if "choice" in objective.lower() or "choice" in tool_name.lower():
                tenant = "Choice Inc"

            context_key = f"NEGOTIATION_{tool_name.upper()}_{int(time.time())}"
            context_value = f"Objective: {objective}: Result: SUCCESS"
            
            log_metadata = {
                "objective": objective,
                "tool_name": tool_name,
                "status": "SUCCESS",
                "request_payload": clean_log_payload,
                "response_payload": redacted_response,
                "latency_ms": elapsed_ms
            }
            self.memory_bank.store_context(context_key, context_value, log_metadata, tenant=tenant)

            return {
                "success": True,
                "response": redacted_response,
                "error": None
            }

        except Exception as err:
            err_msg = str(err)
            sanitized_err = self.vault.redact_data(err_msg)
            sys.stderr.write(f"Negotiation handler execution error: {sanitized_err}\n")

            # Log exception state to local SQLite cache
            tenant = "Goings OS"
            if "choice" in objective.lower() or "choice" in tool_name.lower():
                tenant = "Choice Inc"

            context_key = f"NEGOTIATION_ERROR_{tool_name.upper()}_{int(time.time())}"
            context_value = f"Objective: {objective}: Result: FAILURE"
            
            log_metadata = {
                "objective": objective,
                "tool_name": tool_name,
                "status": "ERROR",
                "request_payload": clean_log_payload,
                "error_message": sanitized_err
            }
            self.memory_bank.store_context(context_key, context_value, log_metadata, tenant=tenant)

            return {
                "success": False,
                "response": None,
                "error": sanitized_err
            }


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS NEGOTIATOR PROTOCOL NODE          ")
    print("==========================================================")
    
    # Simple direct validation trace
    vault = CredentialVault()
    vault.store_credential("GHL_API_KEY", "live_token_secret_123456_key")
    
    node = NegotiatorNode(vault=vault)
    
    # Define a mock CRM sync API endpoint handler
    def mock_crm_handler(payload):
        api_key = payload.get("api_key")
        if api_key != "live_token_secret_123456_key":
            raise ValueError("Unauthorized: Invalid API key credentials")
        return {
            "status": "synchronized",
            "records_updated": 4,
            "secret_response_token": "resp_token_9988_secret"
        }
        
    node.register_tool("crm_sync", mock_crm_handler)
    
    # Store dynamic response token to verify double redaction
    vault.store_credential("RESP_TOKEN", "resp_token_9988_secret")
    
    # Execute negotiation objective with vault reference
    objective = "Sync Choice CRM leads database"
    req_payload = {
        "api_key": "vault://GHL_API_KEY",
        "sync_mode": "incremental"
    }
    
    result = node.execute_negotiation(objective, "crm_sync", req_payload)
    print(f" -> Result Status: {result['success']}")
    print("==========================================================")
