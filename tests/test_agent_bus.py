# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UNIT TESTS FOR AGENT BUS (tests/test_agent_bus.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; ENTERPRISE UNITTEST
# ==============================================================================

import os
import sys
import time
import json
import tempfile
import shutil
import sqlite3
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core_nodes.node_20_agent_bus.agent_bus import (
    InterAgentEventBus,
    ConsensusArbitrator,
    GoogleChatBusSync,
    ConsensusGateBlocked,
    DeadlockDetectedException,
    STANDARD_AGENT_CARDS,
    init_agent_bus_db
)


class TestAgentCards(unittest.TestCase):
    """Verifies Agent2Agent standard card schemas and registrations."""

    def test_standard_cards_structure(self):
        self.assertIn("lexis-secretary", STANDARD_AGENT_CARDS)
        self.assertIn("aegis-risk", STANDARD_AGENT_CARDS)
        self.assertIn("titan-infra", STANDARD_AGENT_CARDS)
        self.assertIn("virtual-payments", STANDARD_AGENT_CARDS)

        for agent_id, card in STANDARD_AGENT_CARDS.items():
            self.assertEqual(card["agent_id"], agent_id)
            self.assertTrue(len(card["capabilities"]) > 0)
            self.assertTrue(len(card["authorized_intents"]) > 0)
            self.assertIn("security_clearance", card)
            self.assertIn("endpoints", card)


class TestConsensusArbitrator(unittest.TestCase):
    """Verifies consensus gate logic and deadlock detection."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_bus.db")
        self.arbitrator = ConsensusArbitrator(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_high_impact_actions_require_aegis_risk(self):
        reviewers = self.arbitrator.determine_required_reviewers("ISSUE_VIRTUAL_CARD", "HIGH")
        self.assertIn("aegis-risk", reviewers)

        statutory_reviewers = self.arbitrator.determine_required_reviewers("SUBMIT_STATUTORY_FILING", "HIGH")
        self.assertIn("aegis-risk", statutory_reviewers)

    def test_verify_consensus_gate_blocks_without_aegis_review(self):
        allowed, msg, token = self.arbitrator.verify_consensus_gate(
            intent_id="intent_123",
            action_name="ISSUE_VIRTUAL_CARD",
            primary_agent="virtual-payments",
            reviews=[]
        )
        self.assertFalse(allowed)
        self.assertIn("requires mandatory sign-off from @aegis-risk", msg)
        self.assertIsNone(token)

    def test_verify_consensus_gate_blocks_on_rejection(self):
        reviews = [
            {
                "reviewer_agent": "aegis-risk",
                "verdict": "REJECTED",
                "review_notes": "Prompt contains suspicious escalation syntax."
            }
        ]
        allowed, msg, token = self.arbitrator.verify_consensus_gate(
            intent_id="intent_123",
            action_name="ISSUE_VIRTUAL_CARD",
            primary_agent="virtual-payments",
            reviews=reviews
        )
        self.assertFalse(allowed)
        self.assertIn("returned verdict 'REJECTED'", msg)
        self.assertIsNone(token)

    def test_verify_consensus_gate_approves_with_aegis_signoff(self):
        reviews = [
            {
                "reviewer_agent": "aegis-risk",
                "verdict": "APPROVED",
                "review_notes": "Statutory fee matches Virginia SCC Schedule."
            }
        ]
        allowed, msg, token = self.arbitrator.verify_consensus_gate(
            intent_id="intent_123",
            action_name="SUBMIT_STATUTORY_FILING",
            primary_agent="lexis-secretary",
            reviews=reviews
        )
        self.assertTrue(allowed)
        self.assertIsNotNone(token)
        self.assertTrue(token.startswith("CONSENSUS_AUTH_"))

        # Verify vault log
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT verdict, consensus_token FROM agent_bus_consensus_log WHERE intent_id = ?", ("intent_123",))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "APPROVED")
        self.assertEqual(row[1], token)

    def test_deadlock_detection_circular_dependency(self):
        pending = [
            {
                "intent_id": "intent_a",
                "sender_agent": "titan-infra",
                "target_agents": ["virtual-payments"],
                "status": "PENDING_REVIEW"
            },
            {
                "intent_id": "intent_b",
                "sender_agent": "virtual-payments",
                "target_agents": ["titan-infra"],
                "status": "PENDING_REVIEW"
            }
        ]
        deadlocks = self.arbitrator.detect_deadlock(pending, timeout_seconds=60.0)
        self.assertTrue(len(deadlocks) > 0)
        self.assertEqual(deadlocks[0]["type"], "CIRCULAR_DEPENDENCY")

    def test_deadlock_detection_timeout_stall(self):
        pending = [
            {
                "intent_id": "intent_stalled",
                "sender_agent": "lexis-secretary",
                "target_agents": ["aegis-risk"],
                "status": "PENDING_REVIEW",
                "created_epoch": time.time() - 45.0
            }
        ]
        deadlocks = self.arbitrator.detect_deadlock(pending, timeout_seconds=30.0)
        self.assertTrue(len(deadlocks) > 0)
        self.assertEqual(deadlocks[0]["type"], "TIMEOUT_STALL")
        self.assertIn("Terrence Goings", deadlocks[0]["remedy"])


class TestGoogleChatBusSync(unittest.TestCase):
    """Verifies Google Chat thread syncing and card payloads."""

    def test_format_event_card_thread_affinity(self):
        syncer = GoogleChatBusSync()
        event = {
            "intent_id": "intent_test_99",
            "sender_agent": "lexis-secretary",
            "action_name": "SUBMIT_STATUTORY_FILING",
            "impact_level": "HIGH",
            "status": "PENDING_REVIEW",
            "target_agents": ["aegis-risk", "virtual-payments"],
            "payload": {"fee_cents": 5000, "entity": "Keep It Goings LLC"}
        }
        card = syncer.format_event_card(event)
        self.assertIn("cardsV2", card)
        self.assertEqual(card["thread"]["threadKey"], "a2a_thread_intent_test_99")
        self.assertIn("A2A BUS: LEXIS-SECRETARY", card["cardsV2"][0]["card"]["header"]["title"])


class TestInterAgentEventBus(unittest.TestCase):
    """Verifies end-to-end event publishing, @mentions, review workflows, and execution gating."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_bus.db")
        self.bus = InterAgentEventBus(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_publish_intent_with_at_mentions(self):
        received_events = []

        def aegis_listener(event):
            received_events.append(event)

        self.bus.subscribe("aegis-risk", aegis_listener)

        evt = self.bus.publish_intent(
            sender_agent="lexis-secretary",
            action_name="GENERATE_REGULATORY_DOC",
            payload={"form": "SCC-LLC-1062", "entity": "Keep It Goings LLC"},
            impact_level="MEDIUM",
            mention_text="Please review statutory document @aegis-risk and @virtual-payments"
        )
        self.assertEqual(evt["sender_agent"], "lexis-secretary")
        self.assertIn("aegis-risk", evt["target_agents"])
        self.assertIn("virtual-payments", evt["target_agents"])
        self.assertEqual(len(received_events), 1)

        # Verify vault event record
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sender_agent, action_name, status FROM agent_bus_events WHERE intent_id = ?", (evt["intent_id"],))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "lexis-secretary")
        self.assertEqual(row[1], "GENERATE_REGULATORY_DOC")

    def test_unregistered_agent_cannot_publish(self):
        with self.assertRaises(ValueError):
            self.bus.publish_intent(
                sender_agent="rogue-external-bot",
                action_name="TAMPER_VAULT",
                payload={}
            )

    def test_submit_peer_review_and_execute_with_consensus(self):
        # 1. Lexis publishes intent requiring card issuance
        intent = self.bus.publish_intent(
            sender_agent="lexis-secretary",
            action_name="ISSUE_VIRTUAL_CARD",
            payload={"merchant": "VA_SCC_CLERK", "amount_cents": 5000},
            impact_level="HIGH"
        )
        intent_id = intent["intent_id"]

        # 2. Execution attempt before Aegis sign-off is blocked
        tool_executed = False

        def mock_tool():
            nonlocal tool_executed
            tool_executed = True
            return {"card_id": "priv_card_12345", "status": "ACTIVE"}

        with self.assertRaises(ConsensusGateBlocked):
            self.bus.execute_with_consensus(intent_id, mock_tool)

        self.assertFalse(tool_executed)

        # 3. Aegis-Risk submits positive review
        review = self.bus.submit_peer_review(
            intent_id=intent_id,
            reviewer_agent="aegis-risk",
            verdict="APPROVED",
            notes="Fee of $50.00 confirmed within authorized statutory schedule."
        )
        self.assertEqual(review["verdict"], "APPROVED")

        # 4. Execution now succeeds
        res = self.bus.execute_with_consensus(intent_id, mock_tool)
        self.assertTrue(tool_executed)
        self.assertEqual(res["status"], "EXECUTED_SUCCESS")
        self.assertTrue(res["consensus_token"].startswith("CONSENSUS_AUTH_"))


if __name__ == "__main__":
    unittest.main()
