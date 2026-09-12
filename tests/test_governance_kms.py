# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UNIT TESTS FOR GOVERNANCE KMS (tests/test_governance_kms.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; ENTERPRISE UNITTEST
# ==============================================================================

import os
import sys
import time
import tempfile
import shutil
import sqlite3
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core_nodes.node_21_governance_kms.governance_kms import (
    GcpKmsKeyManager,
    GlobalPrivacyEngine,
    EuAiActAuditLogger,
    OfacSanctionsScreening,
    EmergencyKillSwitch,
    init_governance_kms_db
)
from core_nodes.node_19_virtual_payments.virtual_payments import VirtualPaymentEngine


class TestGcpKmsKeyManager(unittest.TestCase):
    """Verifies KMS secret storage, integrity checking, decryption, and rotation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_kms.db")
        self.kms = GcpKmsKeyManager(db_path=self.db_path, master_key="test_aegis_kms_key_2026")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_store_and_retrieve_secret(self):
        res = self.kms.store_secret("PRIVACY_COM_API_KEY", "priv_live_secret_token_12345")
        self.assertEqual(res["secret_name"], "PRIVACY_COM_API_KEY")
        self.assertEqual(res["version"], 1)

        retrieved = self.kms.retrieve_secret("PRIVACY_COM_API_KEY")
        self.assertEqual(retrieved, "priv_live_secret_token_12345")

    def test_rotate_secret_creates_new_version(self):
        self.kms.store_secret("STRIPE_SECRET_KEY", "sk_live_version_1")
        v1_val = self.kms.retrieve_secret("STRIPE_SECRET_KEY", version=1)
        self.assertEqual(v1_val, "sk_live_version_1")

        res_v2 = self.kms.rotate_secret("STRIPE_SECRET_KEY", "sk_live_version_2")
        self.assertEqual(res_v2["version"], 2)

        latest_val = self.kms.retrieve_secret("STRIPE_SECRET_KEY")
        self.assertEqual(latest_val, "sk_live_version_2")

    def test_retrieve_nonexistent_secret_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.kms.retrieve_secret("NON_EXISTENT_KEY")


class TestGlobalPrivacyEngine(unittest.TestCase):
    """Verifies VCDPA and GDPR PII/PHI redaction patterns."""

    def test_redact_ssn_and_tin(self):
        prompt = "Onboard client Terrence with SSN 123-45-6789 and EIN 98-7654321."
        sanitized, counts = GlobalPrivacyEngine.redact_pii(prompt)
        self.assertNotIn("123-45-6789", sanitized)
        self.assertIn("[REDACTED_SSN_TIN]", sanitized)
        self.assertTrue(counts.get("ssn", 0) > 0)

    def test_redact_email_and_phone(self):
        prompt = "Contact executive at info@goingsos.com or call 757-555-0199 for verification."
        sanitized, counts = GlobalPrivacyEngine.redact_pii(prompt)
        self.assertNotIn("info@goingsos.com", sanitized)
        self.assertNotIn("757-555-0199", sanitized)
        self.assertIn("[REDACTED_EMAIL]", sanitized)
        self.assertIn("[REDACTED_PHONE]", sanitized)
        self.assertEqual(counts["email"], 1)
        self.assertEqual(counts["phone"], 1)

    def test_redact_financial_pan(self):
        prompt = "Charge card number 4111 2222 3333 4444 for registration fee."
        sanitized, counts = GlobalPrivacyEngine.redact_pii(prompt)
        self.assertNotIn("4111 2222 3333 4444", sanitized)
        self.assertIn("[REDACTED_FINANCIAL_PAN]", sanitized)
        self.assertEqual(counts["credit_card"], 1)


class TestEuAiActAuditLogger(unittest.TestCase):
    """Verifies high-risk AI decision logging and right to explanation lineage."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_eu_ai.db")
        self.logger = EuAiActAuditLogger(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_ai_decision_records_hashes_and_sanitized_prompt(self):
        res = self.logger.log_ai_decision(
            agent_id="lexis-secretary",
            model_engine="gemini-3.8-flash",
            risk_classification="HIGH_RISK_REGULATORY",
            raw_prompt_input="Evaluate filing for client with SSN 001-22-3333.",
            raw_output_decision="Approve Virginia SCC filing form SCC-LLC-1062.",
            right_to_explanation_rationale="Form accurately matches Commonwealth statutory fee schedule with zero late penalties."
        )
        self.assertEqual(res["status"], "LOGGED_COMPLIANT")
        self.assertEqual(res["risk_classification"], "HIGH_RISK_REGULATORY")

        # Verify vault entry and that raw SSN is redacted from lineage
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sanitized_input_lineage, right_to_explanation_rationale FROM eu_ai_act_lineage_log WHERE decision_id = ?", (res["decision_id"],))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertNotIn("001-22-3333", row[0])
        self.assertIn("[REDACTED_SSN_TIN]", row[0])
        self.assertIn("Commonwealth statutory fee schedule", row[1])


class TestOfacSanctionsScreening(unittest.TestCase):
    """Verifies OFAC SDN screening against sanctioned entities and embargoed destinations."""

    def test_screen_legitimate_vendor_cleared(self):
        res = OfacSanctionsScreening.screen_entity("OpenAI LLC", "United States")
        self.assertTrue(res["is_cleared"])
        self.assertEqual(res["status"], "CLEARED")
        self.assertEqual(len(res["matches"]), 0)

    def test_screen_sanctioned_entity_blocked(self):
        res = OfacSanctionsScreening.screen_entity("Al-Qaida Logistics Front", "Global")
        self.assertFalse(res["is_cleared"])
        self.assertEqual(res["status"], "SANCTIONS_BLOCKED")
        self.assertTrue(len(res["matches"]) > 0)
        self.assertIn("AL-QAIDA", res["matches"][0])

    def test_screen_embargoed_country_blocked(self):
        res = OfacSanctionsScreening.screen_entity("Tehran Trade Corp", "Iran")
        self.assertFalse(res["is_cleared"])
        self.assertEqual(res["status"], "SANCTIONS_BLOCKED")
        self.assertTrue(any("IRAN" in m for m in res["matches"]))


class TestEmergencyKillSwitch(unittest.TestCase):
    """Verifies sub-500ms emergency stop, card revocation, and vault locking."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_emergency.db")
        self.kill_switch = EmergencyKillSwitch(db_path=self.db_path)
        # Create virtual payments engine in same db to test card revocation
        self.vpay = VirtualPaymentEngine(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_trigger_emergency_stop_sub_500ms_and_revokes_cards(self):
        # 1. Issue an active card
        card_res = self.vpay.issue_single_use_card(
            entity_name="Keep It Goings LLC",
            merchant_name="Google Cloud",
            amount_cents=800,
            purpose="Routine Cloud compute"
        )
        card_id = card_res["card_id"]

        # 2. Trigger emergency stop
        stop_res = self.kill_switch.trigger_emergency_stop(
            reason="Anomalous prompt injection spike detected on external webhook ingress",
            triggered_by="Terrence Goings, Lead Architect"
        )

        self.assertEqual(stop_res["status"], "SYSTEM_EMERGENCY_LOCKED")
        self.assertTrue(stop_res["sla_met_sub_500ms"])
        self.assertTrue(stop_res["execution_latency_ms"] < 500.0)
        self.assertGreaterEqual(stop_res["cards_revoked_count"], 1)

        # 3. Verify card status transitioned to REVOKED_EMERGENCY
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM virtual_payment_cards WHERE card_id = ?", (card_id,))
        card_status = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(card_status, "REVOKED_EMERGENCY")

        # 4. Verify system lock state
        is_locked, reason = self.kill_switch.check_system_lock_state()
        self.assertTrue(is_locked)
        self.assertIn("Anomalous prompt injection", reason)

        # 5. Test release lock
        release_res = self.kill_switch.release_emergency_lock("Terrence Goings", "Anomaly resolved.")
        self.assertEqual(release_res["status"], "LOCK_RELEASED")
        is_locked_now, _ = self.kill_switch.check_system_lock_state()
        self.assertFalse(is_locked_now)


if __name__ == "__main__":
    unittest.main()
