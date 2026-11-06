import logging
import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s | SENTINEL | %(message)s")

class TaskPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_name: str
    action_type: str
    target_phone: Optional[str] = None
    raw_data: Optional[str] = None
    contains_pii: bool = False

class RegulatorySentinel:
    def __init__(self):
        self.tcpa_start_hour = 8
        self.tcpa_end_hour = 20
        # Regex patterns for active sanitization
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.cc_pattern = re.compile(r'\b(?:\d[ -]*?){13,16}\b')

    def verify_tcpa_compliance(self) -> bool:
        """Physically blocks SMS dispatch outside of 8 AM to 8 PM local time."""
        current_hour = datetime.now().hour
        if self.tcpa_start_hour <= current_hour < self.tcpa_end_hour:
            return True
        logging.warning("TCPA VIOLATION BLOCKED: Attempted to send SMS outside authorized quiet hours.")
        return False

    def sanitize_fcra_data(self, text: str) -> str:
        """Actively scrubs SSNs and Credit Cards to enforce Constitutional data sovereignty."""
        if not text:
            return text
        sanitized = self.ssn_pattern.sub("[REDACTED_SSN]", text)
        sanitized = self.cc_pattern.sub("[REDACTED_CC]", sanitized)
        return sanitized

    def pre_flight_audit(self, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the Legal Trinity audit before allowing Swarm execution."""
        logging.info("Initiating Pre-Flight Legal Trinity Audit...")
        
        try:
            # Enforce strict data contract
            payload = TaskPayload(**raw_payload)
        except Exception as e:
            logging.error(f"UCC CONTRACT VIOLATION: Payload schema rejected. {e}")
            raise ValueError("Invalid payload schema. Execution halted.")

        # 1. TCPA Audit for SMS
        if payload.action_type == 'send_sms':
            if not self.verify_tcpa_compliance():
                raise PermissionError("TCPA Compliance Failure. Task halted.")

        # 2. FCRA and Trinity Audit for PII
        safe_data = payload.raw_data
        if payload.contains_pii and payload.raw_data:
            logging.info("FCRA PROTOCOL ENGAGED: Sanitizing private client data.")
            safe_data = self.sanitize_fcra_data(payload.raw_data)

        logging.info(f"Audit Passed for {payload.entity_name}. Safe to execute.")
        
        # Return the sanitized and verified payload for the Orchestrator to use
        return {
            "entity_name": payload.entity_name,
            "action_type": payload.action_type,
            "target_phone": payload.target_phone,
            "safe_data": safe_data
        }

# Orchestrator Hook
sentinel = RegulatorySentinel()
