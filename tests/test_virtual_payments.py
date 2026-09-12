# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UNIT TESTS FOR VIRTUAL PAYMENTS (tests/test_virtual_payments.py)
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

from core_nodes.node_19_virtual_payments.virtual_payments import (
    VirtualPaymentEngine,
    PrivacyComProvider,
    StripeIssuingProvider,
    SpendControlPolicy,
    AegisSpendLimitExceeded,
    MerchantLockViolation,
    UnauthorizedPaymentRequest,
    BASE_SPEND_CAP_CENTS,
    init_virtual_payments_db
)


class TestSpendControlPolicy(unittest.TestCase):
    """Verifies Aegis spend limits, base thresholds, and authorization logic."""

    def setUp(self):
        self.policy = SpendControlPolicy(base_threshold_cents=1000)

    def test_zero_or_negative_amount_rejected(self):
        allowed, msg = self.policy.evaluate_request(0, "Test micro-charge")
        self.assertFalse(allowed)
        self.assertIn("strictly greater than 0", msg)

        allowed_neg, msg_neg = self.policy.evaluate_request(-500, "Negative charge")
        self.assertFalse(allowed_neg)

    def test_within_base_threshold_approved_automatically(self):
        allowed, msg = self.policy.evaluate_request(850, "Domain lookup API call")
        self.assertTrue(allowed)
        self.assertIn("Approved under base micro-transaction threshold", msg)

    def test_exactly_base_threshold_approved_automatically(self):
        allowed, msg = self.policy.evaluate_request(1000, "Base threshold boundary")
        self.assertTrue(allowed)

    def test_exceeding_base_threshold_without_token_rejected(self):
        allowed, msg = self.policy.evaluate_request(5000, "SCC Annual Registration Fee")
        self.assertFalse(allowed)
        self.assertIn("Aegis-Risk Block", msg)
        self.assertIn("Valid auth token required", msg)

    def test_exceeding_base_threshold_with_invalid_token_prefix_rejected(self):
        allowed, msg = self.policy.evaluate_request(
            5000,
            "SCC Annual Registration Fee",
            auth_token="INVALID_TOKEN_123",
            authorized_by="Terrence Goings"
        )
        self.assertFalse(allowed)
        self.assertIn("Invalid authorization token prefix", msg)

    def test_exceeding_base_threshold_with_unauthorized_person_rejected(self):
        allowed, msg = self.policy.evaluate_request(
            5000,
            "SCC Annual Registration Fee",
            auth_token="AEGIS_AUTH_123456789",
            authorized_by="Junior Developer"
        )
        self.assertFalse(allowed)
        self.assertIn("Sign-off by Terrence Goings required", msg)

    def test_exceeding_base_threshold_with_terrence_goings_approved(self):
        allowed, msg = self.policy.evaluate_request(
            5000,
            "SCC Annual Registration Fee",
            auth_token="AEGIS_AUTH_123456789",
            authorized_by="Terrence Goings, Managing Director"
        )
        self.assertTrue(allowed)
        self.assertIn("Approved via Executive Sign-off", msg)


class TestProviders(unittest.TestCase):
    """Verifies card creation schemas across Privacy.com and Stripe Issuing."""

    def test_privacy_com_card_creation(self):
        provider = PrivacyComProvider()
        card = provider.create_card(
            memo="Keep It Goings LLC - Cloud API",
            spend_limit_cents=900,
            merchant_lock="Google Cloud",
            single_use=True
        )
        self.assertEqual(card["provider"], "PRIVACY_COM")
        self.assertEqual(card["spend_limit_cents"], 900)
        self.assertEqual(card["merchant_lock"], "Google Cloud")
        self.assertEqual(card["card_type"], "SINGLE_USE")
        self.assertTrue(card["pan_masked"].startswith("************"))
        self.assertEqual(card["status"], "ACTIVE")

    def test_stripe_issuing_card_creation(self):
        provider = StripeIssuingProvider()
        card = provider.create_card(
            cardholder_name="Choice Inc",
            spend_limit_cents=1000,
            merchant_lock="IRS Filing Center",
            currency="usd"
        )
        self.assertEqual(card["provider"], "STRIPE_ISSUING")
        self.assertEqual(card["spend_limit_cents"], 1000)
        self.assertEqual(card["merchant_lock"], "IRS Filing Center")
        self.assertEqual(card["currency"], "usd")
        self.assertEqual(card["status"], "ACTIVE")
        self.assertIn("spending_controls", card)


class TestVirtualPaymentEngine(unittest.TestCase):
    """Verifies full payment orchestration, merchant locking, spend limits, and vault persistence."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_vault.db")
        self.engine = VirtualPaymentEngine(db_path=self.db_path, base_threshold_cents=1000)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_issue_base_micro_card_success(self):
        res = self.engine.issue_single_use_card(
            entity_name="Keep It Goings LLC",
            merchant_name="OpenAI API",
            amount_cents=850,
            purpose="Monthly LLM API usage"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["authorized_spend_cents"], 850)
        self.assertEqual(res["merchant_lock"], "OpenAI API")
        self.assertEqual(res["authorized_spend_dollars"], "$8.50")

        # Verify record in vault
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT card_id, merchant_lock, spend_limit_cents, status FROM virtual_payment_cards WHERE card_id = ?", (res["card_id"],))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], res["card_id"])
        self.assertEqual(row[1], "OpenAI API")
        self.assertEqual(row[2], 850)
        self.assertEqual(row[3], "ACTIVE")

    def test_issue_card_exceeding_base_without_auth_raises_exception(self):
        with self.assertRaises(AegisSpendLimitExceeded):
            self.engine.issue_single_use_card(
                entity_name="The Goings Group LLC",
                merchant_name="VA_SCC_CLERK",
                amount_cents=5000,
                purpose="Annual Registration"
            )

    def test_issue_statutory_filing_card_with_executive_token(self):
        filing_record = {
            "entity_name": "Keep It Goings LLC",
            "filing_fee_cents": 5000,
            "max_authorized_fee_cents": 5000,
            "jurisdiction": "VA_SCC",
            "filing_type": "ANNUAL_REGISTRATION_SCC_1062"
        }
        res = self.engine.issue_statutory_filing_card(
            filing_record=filing_record,
            authorized_by="Terrence Goings",
            auth_token="AEGIS_AUTH_789456123"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["merchant_lock"], "VA_SCC_CLERK")
        self.assertEqual(res["authorized_spend_cents"], 5000)
        self.assertEqual(res["authorized_spend_dollars"], "$50.00")

    def test_statutory_filing_card_fails_if_fee_exceeds_max(self):
        filing_record = {
            "entity_name": "Keep It Goings LLC",
            "filing_fee_cents": 7500,
            "max_authorized_fee_cents": 5000,
            "jurisdiction": "VA_SCC"
        }
        with self.assertRaises(AegisSpendLimitExceeded):
            self.engine.issue_statutory_filing_card(
                filing_record=filing_record,
                authorized_by="Terrence Goings",
                auth_token="AEGIS_AUTH_789456123"
            )

    def test_process_card_transaction_success_closes_single_use_card(self):
        res = self.engine.issue_single_use_card(
            entity_name="Keep It Goings LLC",
            merchant_name="Google Cloud",
            amount_cents=950,
            purpose="Compute Engine micro-instance"
        )
        card_id = res["card_id"]

        # Charge matching merchant and amount <= limit
        tx = self.engine.process_card_transaction(
            card_id=card_id,
            merchant_name="Google Cloud",
            charge_amount_cents=950
        )
        self.assertEqual(tx["status"], "SETTLED")
        self.assertEqual(tx["card_status_now"], "CLOSED")
        self.assertTrue(tx["authorization_code"].startswith("AUTH_"))

        # Vault checks
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM virtual_payment_cards WHERE card_id = ?", (card_id,))
        self.assertEqual(cursor.fetchone()[0], "CLOSED")

        cursor.execute("SELECT card_id, amount_cents, status FROM virtual_payment_transactions WHERE card_id = ?", (card_id,))
        tx_row = cursor.fetchone()
        conn.close()
        self.assertEqual(tx_row[0], card_id)
        self.assertEqual(tx_row[1], 950)
        self.assertEqual(tx_row[2], "SETTLED")

    def test_process_card_transaction_merchant_lock_violation(self):
        res = self.engine.issue_single_use_card(
            entity_name="Keep It Goings LLC",
            merchant_name="VA_SCC_CLERK",
            amount_cents=500,
            purpose="Registry check"
        )
        card_id = res["card_id"]

        with self.assertRaises(MerchantLockViolation):
            self.engine.process_card_transaction(
                card_id=card_id,
                merchant_name="Amazon Web Services",
                charge_amount_cents=500
            )

    def test_process_card_transaction_spend_limit_exceeded(self):
        res = self.engine.issue_single_use_card(
            entity_name="Keep It Goings LLC",
            merchant_name="VA_SCC_CLERK",
            amount_cents=800,
            purpose="Registry fee"
        )
        card_id = res["card_id"]

        with self.assertRaises(AegisSpendLimitExceeded):
            self.engine.process_card_transaction(
                card_id=card_id,
                merchant_name="VA_SCC_CLERK",
                charge_amount_cents=900
            )

    def test_cannot_reuse_closed_single_use_card(self):
        res = self.engine.issue_single_use_card(
            entity_name="Keep It Goings LLC",
            merchant_name="Anthropic API",
            amount_cents=700,
            purpose="API call"
        )
        card_id = res["card_id"]

        # First charge settles and closes card
        self.engine.process_card_transaction(
            card_id=card_id,
            merchant_name="Anthropic API",
            charge_amount_cents=700
        )

        # Second charge attempts on closed card
        with self.assertRaises(ValueError):
            self.engine.process_card_transaction(
                card_id=card_id,
                merchant_name="Anthropic API",
                charge_amount_cents=100
            )


if __name__ == "__main__":
    unittest.main()
