# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: INTER-AGENT EVENT BUS & A2A PROTOCOL (core_nodes/node_20_agent_bus/agent_bus.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; AEGIS PEER CONSENSUS; WAL CONCURRENCY
# ==============================================================================

import os
import sys
import time
import json
import uuid
import hmac
import hashlib
import sqlite3
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple, Callable

ROOT_DIR = os.environ.get("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

data_vault = os.path.join(ROOT_DIR, "data", "goings_os_vault.db")
DB_PATH = data_vault if os.path.exists(data_vault) else os.path.join(ROOT_DIR, "goings_os_vault.db")

GOOGLE_CHAT_AGENT_BUS_WEBHOOK = os.environ.get("GOOGLE_CHAT_AGENT_BUS_WEBHOOK", "")

# ==============================================================================
# 1. DATABASE SCHEMA INITIALIZATION
# ==============================================================================

def init_agent_bus_db(db_path: str = DB_PATH) -> None:
    """Initializes inter-agent event bus and consensus tables in SQLite vault."""
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_bus_events (
                event_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL,
                sender_agent TEXT NOT NULL,
                event_type TEXT NOT NULL,
                action_name TEXT NOT NULL,
                target_agents TEXT NOT NULL,
                payload JSON NOT NULL,
                impact_level TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_bus_consensus_log (
                consensus_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL,
                action_name TEXT NOT NULL,
                primary_agent TEXT NOT NULL,
                required_reviewer TEXT NOT NULL,
                reviewer_agent TEXT NOT NULL,
                verdict TEXT NOT NULL,
                consensus_token TEXT,
                review_notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (intent_id) REFERENCES agent_bus_events(intent_id)
            );
        """)
        conn.commit()
        conn.close()
    except Exception as err:
        logging.error(f"Failed to initialize agent bus schema in vault: {str(err)}")


init_agent_bus_db()

# ==============================================================================
# 2. AGENT2AGENT (A2A) PROTOCOL STANDARD: AGENT CARDS
# ==============================================================================

STANDARD_AGENT_CARDS: Dict[str, Dict[str, Any]] = {
    "lexis-secretary": {
        "agent_id": "lexis-secretary",
        "name": "Lexis-Secretary Agent",
        "node_id": "node_18_lexis_secretary",
        "role": "Corporate Secretary & Regulatory Compliance",
        "security_clearance": "REGULATORY_FILING",
        "capabilities": [
            "scc_annual_report_monitoring",
            "fincen_boir_tracking",
            "municipal_bpol_assessment",
            "regulatory_document_generation"
        ],
        "endpoints": {
            "mcp_tool": "verify_statutory_filing",
            "module": "core_nodes.node_18_lexis_secretary.lexis_secretary"
        },
        "authorized_intents": [
            "SCAN_COMPLIANCE",
            "GENERATE_REGULATORY_DOC",
            "REQUEST_FILING_APPROVAL"
        ]
    },
    "aegis-risk": {
        "agent_id": "aegis-risk",
        "name": "Aegis-Risk Governance Agent",
        "node_id": "middleware_model_armor",
        "role": "Chief Risk Officer, Prompt Armor & Consensus Gatekeeper",
        "security_clearance": "EXECUTIVE_OVERSIGHT",
        "capabilities": [
            "cryptographic_token_validation",
            "spend_ceiling_enforcement",
            "prompt_injection_sanitization",
            "deadlock_arbitration",
            "statutory_consensus_signoff"
        ],
        "endpoints": {
            "mcp_tool": "record_executive_order",
            "module": "middleware.model_armor"
        },
        "authorized_intents": [
            "EVALUATE_RISK",
            "ARBITRATE_DEADLOCK",
            "SIGN_OFF_CONSENSUS",
            "BLOCK_EXECUTION"
        ]
    },
    "titan-infra": {
        "agent_id": "titan-infra",
        "name": "Titan-Infra Autonomous Deployer",
        "node_id": "node_17_auto_updater",
        "role": "Infrastructure Reliability & Self-Healing Deployments",
        "security_clearance": "INFRA_DEPLOYMENT",
        "capabilities": [
            "upstream_dependency_monitoring",
            "isolated_branch_patching",
            "self_healing_pytest_execution",
            "multi_channel_alerting"
        ],
        "endpoints": {
            "http_callback": "/api/v4.2/deploy/approve",
            "module": "core_nodes.node_17_auto_updater.auto_updater"
        },
        "authorized_intents": [
            "POLL_DEPENDENCIES",
            "STAGE_PATCH_BRANCH",
            "REQUEST_DEPLOY_APPROVAL"
        ]
    },
    "virtual-payments": {
        "agent_id": "virtual-payments",
        "name": "Virtual-Payments Engine",
        "node_id": "node_19_virtual_payments",
        "role": "Autonomous Card Issuance & Spend Control Enforcement",
        "security_clearance": "FINANCIAL_DISBURSEMENT",
        "capabilities": [
            "merchant_locked_card_issuance",
            "single_use_virtual_pan_generation",
            "hard_spend_ceiling_enforcement",
            "vault_transaction_settlement"
        ],
        "endpoints": {
            "mcp_tool": "issue_virtual_card",
            "module": "core_nodes.node_19_virtual_payments.virtual_payments"
        },
        "authorized_intents": [
            "ISSUE_CARD",
            "SETTLE_TRANSACTION",
            "ENFORCE_SPEND_CAP"
        ]
    }
}


# ==============================================================================
# 3. CONSENSUS & DEADLOCK ARBITRATION
# ==============================================================================

class ConsensusGateBlocked(Exception):
    """Raised when an action is executed without required peer verification."""
    pass


class DeadlockDetectedException(Exception):
    """Raised when circular review dependencies or timeout stalls occur."""
    pass


class ConsensusArbitrator:
    """Enforces Aegis-Risk peer sign-off rules and arbitrates review deadlocks."""

    HIGH_IMPACT_ACTIONS = {
        "ISSUE_VIRTUAL_CARD",
        "DISBURSE_FUNDS",
        "SUBMIT_STATUTORY_FILING",
        "DEPLOY_INFRA_BRANCH",
        "DELETE_VAULT_RECORDS"
    }

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_agent_bus_db(self.db_path)

    def determine_required_reviewers(self, action_name: str, impact_level: str) -> List[str]:
        """Calculates required peer reviewers. High-impact actions strictly require aegis-risk."""
        impact = impact_level.upper()
        if action_name in self.HIGH_IMPACT_ACTIONS or impact in ("HIGH", "CRITICAL"):
            return ["aegis-risk"]
        if impact == "MEDIUM":
            return ["aegis-risk"]
        return []

    def verify_consensus_gate(
        self,
        intent_id: str,
        action_name: str,
        primary_agent: str,
        reviews: List[Dict[str, Any]]
    ) -> Tuple[bool, str, Optional[str]]:
        """Validates that all mandatory peer approvals are present before action executes."""
        required = self.determine_required_reviewers(action_name, "HIGH" if action_name in self.HIGH_IMPACT_ACTIONS else "LOW")
        if not required:
            return True, "No mandatory peer review required for low-impact action.", None

        # Check Aegis-Risk sign-off
        aegis_review = next((r for r in reviews if r.get("reviewer_agent") == "aegis-risk"), None)
        if not aegis_review:
            msg = f"Aegis-Risk Consensus Block: Action '{action_name}' requires mandatory sign-off from @aegis-risk."
            return False, msg, None

        if aegis_review.get("verdict") != "APPROVED":
            msg = f"Aegis-Risk Consensus Block: @aegis-risk returned verdict '{aegis_review.get('verdict')}': {aegis_review.get('review_notes')}"
            return False, msg, None

        # Generate consensus execution token
        token_seed = f"{intent_id}:{action_name}:{primary_agent}:{time.time()}"
        consensus_token = f"CONSENSUS_AUTH_{hashlib.sha256(token_seed.encode('utf-8')).hexdigest()[:24].upper()}"

        # Persist consensus in vault
        self._record_consensus(
            intent_id=intent_id,
            action_name=action_name,
            primary_agent=primary_agent,
            required_reviewer="aegis-risk",
            reviewer_agent="aegis-risk",
            verdict="APPROVED",
            consensus_token=consensus_token,
            notes=aegis_review.get("review_notes", "Aegis-Risk automated verification confirmed.")
        )

        return True, "Consensus successfully established with @aegis-risk.", consensus_token

    def detect_deadlock(self, pending_intents: List[Dict[str, Any]], timeout_seconds: float = 30.0) -> List[Dict[str, Any]]:
        """Identifies circular dependencies or long-pending stalls across agent intents."""
        now = time.time()
        deadlocks: List[Dict[str, Any]] = []

        # 1. Timeout detection
        for intent in pending_intents:
            created_epoch = intent.get("created_epoch", now)
            elapsed = now - created_epoch
            if elapsed > timeout_seconds and intent.get("status") == "PENDING_REVIEW":
                deadlocks.append({
                    "intent_id": intent.get("intent_id"),
                    "type": "TIMEOUT_STALL",
                    "elapsed_seconds": elapsed,
                    "waiting_on": intent.get("target_agents", []),
                    "remedy": "Escalate to Managing Director Terrence Goings via HitL Gate."
                })

        # 2. Circular dependency check
        # A waits on B while B waits on A
        waiting_map: Dict[str, str] = {}
        for intent in pending_intents:
            sender = intent.get("sender_agent", "")
            targets = intent.get("target_agents", [])
            if targets and intent.get("status") == "PENDING_REVIEW":
                waiting_map[sender] = targets[0]

        for agent, target in waiting_map.items():
            if waiting_map.get(target) == agent:
                deadlocks.append({
                    "type": "CIRCULAR_DEPENDENCY",
                    "cycle": f"{agent} <-> {target}",
                    "remedy": "Aegis-Risk automatic priority override: Aegis-Risk assumes decision authority."
                })

        return deadlocks

    def _record_consensus(
        self,
        intent_id: str,
        action_name: str,
        primary_agent: str,
        required_reviewer: str,
        reviewer_agent: str,
        verdict: str,
        consensus_token: str,
        notes: str
    ) -> None:
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                INSERT OR REPLACE INTO agent_bus_consensus_log (
                    consensus_id, intent_id, action_name, primary_agent,
                    required_reviewer, reviewer_agent, verdict, consensus_token,
                    review_notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"cns_{uuid.uuid4().hex[:12]}", intent_id, action_name, primary_agent,
                required_reviewer, reviewer_agent, verdict, consensus_token, notes,
                time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            ))
            conn.commit()
            conn.close()
        except Exception as err:
            logging.error(f"Failed to record consensus in vault: {str(err)}")


# ==============================================================================
# 4. UNIFIED GOOGLE CHAT SPACE SYNC
# ==============================================================================

class GoogleChatBusSync:
    """Streams inter-agent bus events and peer review dialogues into Google Chat Space."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or GOOGLE_CHAT_AGENT_BUS_WEBHOOK

    def format_event_card(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Constructs Google Chat Card v2 for an inter-agent bus event with thread affinity."""
        sender = event.get("sender_agent", "unknown")
        action = event.get("action_name", "UNKNOWN_ACTION")
        intent_id = event.get("intent_id", "INTENT_UNKNOWN")
        impact = event.get("impact_level", "NORMAL")
        status = event.get("status", "PUBLISHED")
        targets = ", ".join(event.get("target_agents", [])) or "All Agents"
        payload_preview = json.dumps(event.get("payload", {}), indent=2)[:400]

        severity_color = "#D9381E" if impact in ("CRITICAL", "HIGH") else "#F4B400" if impact == "MEDIUM" else "#1A73E8"

        card = {
            "cardsV2": [
                {
                    "cardId": f"bus_event_{intent_id}",
                    "card": {
                        "header": {
                            "title": f"A2A BUS: {sender.upper()} -> {action}",
                            "subtitle": f"Intent: {intent_id} | Impact: {impact}",
                            "imageUrl": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/hub/default/48px.svg",
                            "imageType": "CIRCLE"
                        },
                        "sections": [
                            {
                                "header": "Inter-Agent Dialogue & Routing",
                                "widgets": [
                                    {
                                        "decoratedText": {
                                            "topLabel": "Originating Agent",
                                            "text": f"<b>@{sender}</b>",
                                            "bottomLabel": f"Target Reviewers: {targets}"
                                        }
                                    },
                                    {
                                        "decoratedText": {
                                            "topLabel": "Execution Status",
                                            "text": f"<b>{status}</b>",
                                            "bottomLabel": f"Impact Classification: {impact}"
                                        }
                                    },
                                    {
                                        "textParagraph": {
                                            "text": f"<b>Action Payload:</b><br><font color=\"#666666\"><pre>{payload_preview}</pre></font>"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ],
            "thread": {
                "threadKey": f"a2a_thread_{intent_id}"
            }
        }
        return card

    def broadcast_to_chat(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches event to live Google Chat webhook or records simulated payload."""
        card_payload = self.format_event_card(event)

        if not self.webhook_url:
            logging.info("Google Chat Agent Bus webhook not set; simulated card created.")
            return {"status": "SIMULATED", "channel": "google_chat_bus", "payload": card_payload}

        try:
            req_data = json.dumps(card_payload).encode("utf-8")
            req = urllib.request.Request(
                self.webhook_url,
                data=req_data,
                headers={"Content-Type": "application/json; charset=UTF-8"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                resp_data = resp.read().decode("utf-8")
                return {"status": "DELIVERED", "channel": "google_chat_bus", "response": resp_data}
        except Exception as err:
            logging.error(f"Failed to stream event to Google Chat: {str(err)}")
            return {"status": "ERROR", "error": str(err), "payload": card_payload}


# ==============================================================================
# 5. INTER-AGENT EVENT BUS ENGINE
# ==============================================================================

class InterAgentEventBus:
    """Core Event-Driven Inter-Agent Channel with @mention parsing and consensus gates."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        chat_webhook: Optional[str] = None,
        agent_cards: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        self.db_path = db_path or DB_PATH
        self.cards = agent_cards or STANDARD_AGENT_CARDS
        self.arbitrator = ConsensusArbitrator(db_path=self.db_path)
        self.chat_sync = GoogleChatBusSync(webhook_url=chat_webhook)
        self.subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self.pending_intents: Dict[str, Dict[str, Any]] = {}
        self.intent_reviews: Dict[str, List[Dict[str, Any]]] = {}
        init_agent_bus_db(self.db_path)

    def register_agent_card(self, card: Dict[str, Any]) -> None:
        """Registers or updates an Agent Card in the protocol registry."""
        agent_id = card.get("agent_id")
        if not agent_id:
            raise ValueError("Agent card must contain a unique 'agent_id'.")
        self.cards[agent_id] = card

    def get_agent_card(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves card specifications for an agent."""
        return self.cards.get(agent_id)

    def list_agent_cards(self) -> List[Dict[str, Any]]:
        """Returns all registered agent cards."""
        return list(self.cards.values())

    def subscribe(self, agent_id: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribes an agent handler to the bus for inbound events and mentions."""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)

    def publish_intent(
        self,
        sender_agent: str,
        action_name: str,
        payload: Dict[str, Any],
        impact_level: str = "MEDIUM",
        mention_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Publishes an intent to the bus, parses @mentions, and establishes review requirements."""
        if sender_agent not in self.cards:
            raise ValueError(f"Unregistered agent '{sender_agent}' cannot publish intents.")

        intent_id = f"intent_{uuid.uuid4().hex[:12]}"
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now = time.time()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now))

        # Parse @mentions
        target_agents: List[str] = []
        if mention_text:
            for word in mention_text.split():
                if word.startswith("@"):
                    cleaned = word.lstrip("@").strip(",.:;").lower()
                    if cleaned in self.cards and cleaned not in target_agents:
                        target_agents.append(cleaned)

        # High-impact actions always mandate @aegis-risk
        if action_name in ConsensusArbitrator.HIGH_IMPACT_ACTIONS:
            if "aegis-risk" not in target_agents:
                target_agents.append("aegis-risk")

        event = {
            "event_id": event_id,
            "intent_id": intent_id,
            "sender_agent": sender_agent,
            "event_type": "INTENT_PUBLISHED",
            "action_name": action_name,
            "target_agents": target_agents,
            "payload": payload,
            "impact_level": impact_level.upper(),
            "status": "PENDING_REVIEW" if target_agents else "READY_FOR_EXECUTION",
            "created_at": timestamp,
            "created_epoch": now
        }

        # Store pending intent
        self.pending_intents[intent_id] = event
        self.intent_reviews[intent_id] = []

        # Vault persistence
        self._record_event_in_vault(event)

        # Stream to Google Chat
        chat_res = self.chat_sync.broadcast_to_chat(event)
        event["chat_sync"] = chat_res

        # Notify subscribed handlers
        for target in target_agents:
            if target in self.subscribers:
                for handler in self.subscribers[target]:
                    try:
                        handler(event)
                    except Exception as handler_err:
                        logging.error(f"Subscriber handler error for {target}: {str(handler_err)}")

        return event

    def submit_peer_review(
        self,
        intent_id: str,
        reviewer_agent: str,
        verdict: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Records peer agent review decision for a pending intent."""
        if reviewer_agent not in self.cards:
            raise ValueError(f"Unregistered agent '{reviewer_agent}' cannot submit reviews.")

        if intent_id not in self.pending_intents:
            raise ValueError(f"Intent {intent_id} not found in active bus registry.")

        verdict_clean = verdict.upper()
        if verdict_clean not in ("APPROVED", "REJECTED", "REVISION_REQUESTED"):
            raise ValueError("Verdict must be APPROVED, REJECTED, or REVISION_REQUESTED.")

        review_entry = {
            "intent_id": intent_id,
            "reviewer_agent": reviewer_agent,
            "verdict": verdict_clean,
            "review_notes": notes,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

        self.intent_reviews[intent_id].append(review_entry)

        # Stream review update to Google Chat
        parent_intent = self.pending_intents[intent_id]
        review_event = {
            "intent_id": intent_id,
            "sender_agent": reviewer_agent,
            "event_type": "PEER_REVIEW_SUBMITTED",
            "action_name": parent_intent["action_name"],
            "target_agents": [parent_intent["sender_agent"]],
            "payload": review_entry,
            "impact_level": parent_intent["impact_level"],
            "status": f"REVIEW_{verdict_clean}"
        }
        self.chat_sync.broadcast_to_chat(review_event)

        return review_entry

    def execute_with_consensus(self, intent_id: str, execution_fn: Callable[[], Any]) -> Dict[str, Any]:
        """Enforces Aegis-Risk consensus gate before invoking the actual tool execution function."""
        if intent_id not in self.pending_intents:
            raise ValueError(f"Intent {intent_id} not found in active bus registry.")

        intent = self.pending_intents[intent_id]
        reviews = self.intent_reviews.get(intent_id, [])

        # Verify consensus
        allowed, reason, token = self.arbitrator.verify_consensus_gate(
            intent_id=intent_id,
            action_name=intent["action_name"],
            primary_agent=intent["sender_agent"],
            reviews=reviews
        )

        if not allowed:
            intent["status"] = "CONSENSUS_BLOCKED"
            self._update_event_status(intent["event_id"], "CONSENSUS_BLOCKED")
            raise ConsensusGateBlocked(reason)

        # Execute payload action
        start_time = time.time()
        try:
            result = execution_fn()
            execution_status = "EXECUTED_SUCCESS"
        except Exception as exec_err:
            result = {"error": str(exec_err)}
            execution_status = "EXECUTION_FAILED"

        intent["status"] = execution_status
        self._update_event_status(intent["event_id"], execution_status)

        # Stream final execution to Google Chat
        completion_event = {
            "intent_id": intent_id,
            "sender_agent": "bus-consensus-engine",
            "event_type": "ACTION_COMPLETED",
            "action_name": intent["action_name"],
            "target_agents": [intent["sender_agent"]],
            "payload": {
                "consensus_token": token,
                "execution_time_seconds": round(time.time() - start_time, 4),
                "status": execution_status
            },
            "impact_level": intent["impact_level"],
            "status": execution_status
        }
        self.chat_sync.broadcast_to_chat(completion_event)

        return {
            "intent_id": intent_id,
            "status": execution_status,
            "consensus_token": token,
            "result": result
        }

    # ==============================================================================
    # 6. VAULT DATABASE HELPERS
    # ==============================================================================

    def _record_event_in_vault(self, event: Dict[str, Any]) -> None:
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                INSERT OR REPLACE INTO agent_bus_events (
                    event_id, intent_id, sender_agent, event_type, action_name,
                    target_agents, payload, impact_level, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event["event_id"], event["intent_id"], event["sender_agent"],
                event["event_type"], event["action_name"], json.dumps(event["target_agents"]),
                json.dumps(event["payload"]), event["impact_level"], event["status"],
                event["created_at"]
            ))
            conn.commit()
            conn.close()
        except Exception as err:
            logging.error(f"Failed to record event in vault: {str(err)}")

    def _update_event_status(self, event_id: str, status: str) -> None:
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                UPDATE agent_bus_events SET status = ? WHERE event_id = ?
            """, (status, event_id))
            conn.commit()
            conn.close()
        except Exception as err:
            logging.error(f"Failed to update event status: {str(err)}")
