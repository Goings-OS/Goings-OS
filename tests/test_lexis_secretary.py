# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UNIT TESTS FOR LEXIS SECRETARY (tests/test_lexis_secretary.py)
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

from core_nodes.node_18_lexis_secretary.lexis_secretary import (
    CONGLOMERATE_ENTITIES,
    ComplianceScanner,
    RegulatoryDocumentGenerator,
    HitLEscalationGate,
    LexisSecretaryEngine
)


class TestComplianceScanner(unittest.TestCase):
    """Verifies statutory compliance scanning across state, federal, and municipal authorities."""

    def setUp(self):
        self.scanner = ComplianceScanner()

    def test_scan_virginia_scc_deadlines(self):
        records = self.scanner.scan_virginia_scc_deadlines(reference_year=2026)
        self.assertEqual(len(records), 6)
        
        # Check Luxury Decor & Rentals special anniversary logic
        ldr = next(r for r in records if r["entity_id"] == "ENT_LDR_005")
        self.assertEqual(ldr["statutory_due_date"], "2027-09-30")
        self.assertEqual(ldr["statutory_fee_cents"], 5000)

        # Check Keep It Goings LLC
        kig = next(r for r in records if r["entity_id"] == "ENT_KIG_001")
        self.assertEqual(kig["statutory_due_date"], "2026-07-31")
        self.assertEqual(kig["jurisdiction"], "VA_SCC")

    def test_scan_fincen_boir_requirements(self):
        boir_list = self.scanner.scan_fincen_boir_requirements()
        self.assertEqual(len(boir_list), 6)

        # Choice Inc 501(c)(3) must be exempt under CTA Section 5336(a)(11)(B)(xix)
        choice = next(b for b in boir_list if b["entity_id"] == "ENT_CHOICE_004")
        self.assertTrue(choice["is_exempt"])
        self.assertFalse(choice["requires_filing"])
        self.assertIn("501(c)(3)", choice["exemption_basis"])

        # Commercial LLCs require reporting
        kig = next(b for b in boir_list if b["entity_id"] == "ENT_KIG_001")
        self.assertFalse(kig["is_exempt"])
        self.assertTrue(kig["requires_filing"])

    def test_scan_municipal_bpol_deadlines(self):
        bpol_list = self.scanner.scan_municipal_bpol_deadlines(reference_year=2027)
        self.assertEqual(len(bpol_list), 6)
        for bpol in bpol_list:
            self.assertEqual(bpol["statutory_due_date"], "2027-03-01")
            self.assertIn(bpol["jurisdiction"], ["PORTSMOUTH_CITY", "NEWPORT_NEWS_CITY"])

    def test_execute_full_compliance_audit(self):
        audit = self.scanner.execute_full_compliance_audit()
        self.assertEqual(audit["total_entities"], 6)
        self.assertEqual(len(audit["scc_annual_filings"]), 6)
        self.assertEqual(len(audit["fincen_boir_filings"]), 6)
        self.assertEqual(len(audit["municipal_bpol_filings"]), 6)


class TestRegulatoryDocumentGenerator(unittest.TestCase):
    """Verifies regulatory document auto-filling and statutory fee schedule calculations."""

    def setUp(self):
        self.generator = RegulatoryDocumentGenerator()

    def test_generate_va_scc_annual_registration(self):
        form = self.generator.generate_va_scc_annual_registration("Keep It Goings LLC")
        self.assertEqual(form["form_code"], "SCC-LLC-1062")
        self.assertEqual(form["state_id"], "S1088421")
        self.assertEqual(form["filing_fee_cents"], 5000)
        self.assertEqual(form["max_authorized_fee_cents"], 7500)
        self.assertEqual(form["status"], "DRAFTED")

    def test_generate_fincen_boir_form_exempt(self):
        form = self.generator.generate_fincen_boir_form("Choice Inc (choiceincva.org)")
        self.assertEqual(form["form_code"], "FINCEN-BOIR-500")
        self.assertTrue(form["is_exempt"])
        self.assertEqual(form["reporting_status"], "EXEMPT_RECORD_ARCHIVED")
        self.assertEqual(form["filing_fee_cents"], 0)

    def test_generate_fincen_boir_form_non_exempt(self):
        form = self.generator.generate_fincen_boir_form("Keep It Goings LLC")
        self.assertFalse(form["is_exempt"])
        self.assertEqual(form["reporting_status"], "INITIAL_REPORT_REQUIRED")
        self.assertEqual(form["filing_fee_cents"], 0)

    def test_calculate_bpol_schedule_portsmouth_tiers(self):
        # Under $50k gross receipts: flat $30 fee
        low_rev = self.generator.calculate_bpol_schedule("Keep It Goings LLC", gross_receipts_cents=4000000)
        self.assertEqual(low_rev["filing_fee_dollars"], 30.0)
        self.assertEqual(low_rev["filing_fee_cents"], 3000)

        # Over $50k gross receipts: $0.20 per $100 ($200 on $100k)
        high_rev = self.generator.calculate_bpol_schedule("Keep It Goings LLC", gross_receipts_cents=10000000)
        self.assertEqual(high_rev["filing_fee_dollars"], 200.0)
        self.assertEqual(high_rev["filing_fee_cents"], 20000)
        self.assertTrue(high_rev["max_authorized_fee_cents"] > 20000)

    def test_calculate_bpol_schedule_newport_news_tiers(self):
        # Under $100k gross receipts: flat $50 fee
        low_rev = self.generator.calculate_bpol_schedule("TBE-OS (Tanita Brinkley Enterprises LLC)", gross_receipts_cents=8000000)
        self.assertEqual(low_rev["filing_fee_dollars"], 50.0)

        # Over $100k gross receipts: $0.16 per $100 ($320 on $200k)
        high_rev = self.generator.calculate_bpol_schedule("TBE-OS (Tanita Brinkley Enterprises LLC)", gross_receipts_cents=20000000)
        self.assertEqual(high_rev["filing_fee_dollars"], 320.0)

    def test_unknown_entity_raises_error(self):
        with self.assertRaises(ValueError):
            self.generator.generate_va_scc_annual_registration("Nonexistent Corporation")


class TestHitLEscalationGate(unittest.TestCase):
    """Verifies Aegis-Risk Human-in-the-Loop decision cards and executive sign-off gate."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_vault.db")
        self.gate = HitLEscalationGate(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_aegis_auth_token(self):
        token = self.gate.generate_aegis_auth_token("file-123", "Keep It Goings LLC")
        self.assertTrue(token.startswith("AEGIS_AUTH_"))

    def test_render_google_chat_card(self):
        record = {
            "filing_id": "filing_abc_01",
            "entity_name": "Keep It Goings LLC",
            "filing_fee_cents": 5000,
            "max_authorized_fee_cents": 7500,
            "due_date": "2026-07-31",
            "form_name": "VA SCC Annual Statement"
        }
        card = self.gate.render_google_chat_card(record)
        self.assertIn("cardsV2", card)
        sections = card["cardsV2"][0]["card"]["sections"]
        self.assertEqual(len(sections), 2)
        self.assertIn("Keep It Goings LLC", str(sections[0]))
        self.assertIn("AUTHORIZE STATUTORY FILING", str(sections[1]))

    def test_render_telegram_alert(self):
        record = {
            "entity_name": "Keep It Goings LLC",
            "form_name": "VA SCC Annual Statement",
            "filing_fee_cents": 5000,
            "due_date": "2026-07-31"
        }
        tele = self.gate.render_telegram_alert(record)
        self.assertIn("LEXIS-SECRETARY HITL GATE", tele["text"])
        self.assertIn("inline_keyboard", tele["reply_markup"])

    def test_verify_and_execute_approval_success(self):
        record = {
            "filing_id": "file_test_99",
            "entity_name": "Keep It Goings LLC",
            "jurisdiction": "VA_SCC",
            "filing_type": "ANNUAL_REPORT",
            "statutory_due_date": "2026-07-31",
            "filing_fee_cents": 5000,
            "max_authorized_fee_cents": 7500
        }
        token = self.gate.generate_aegis_auth_token("file_test_99", "Keep It Goings LLC")
        res = self.gate.verify_and_execute_approval(
            record=record,
            approved_by="Terrence Goings",
            auth_token=token
        )
        self.assertEqual(res["status"], "EXECUTED")
        self.assertEqual(res["hitl_approval"]["approved_by"], "Terrence Goings")

        # Verify vault persistence
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT entity_name, status, approved_by FROM lexis_statutory_filings WHERE filing_id = ?", ("file_test_99",))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Keep It Goings LLC")
        self.assertEqual(row[1], "EXECUTED")
        self.assertEqual(row[2], "Terrence Goings")

    def test_verify_and_execute_approval_unauthorized_approver(self):
        record = {"filing_fee_cents": 5000, "max_authorized_fee_cents": 7500}
        with self.assertRaises(PermissionError):
            self.gate.verify_and_execute_approval(
                record=record,
                approved_by="Random Unauthorized User",
                auth_token="AEGIS_AUTH_XYZ_123"
            )

    def test_verify_and_execute_approval_fee_exceeds_ceiling(self):
        record = {"filing_fee_cents": 10000, "max_authorized_fee_cents": 7500}
        with self.assertRaises(ValueError):
            self.gate.verify_and_execute_approval(
                record=record,
                approved_by="Terrence Goings",
                auth_token="AEGIS_AUTH_XYZ_123"
            )

    def test_verify_and_execute_approval_invalid_token(self):
        record = {"filing_fee_cents": 5000, "max_authorized_fee_cents": 7500}
        with self.assertRaises(ValueError):
            self.gate.verify_and_execute_approval(
                record=record,
                approved_by="Terrence Goings",
                auth_token="INVALID_TOKEN_FORMAT"
            )


class TestLexisSecretaryEngine(unittest.TestCase):
    """Verifies end-to-end corporate secretary engine orchestration."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_vault.db")
        self.engine = LexisSecretaryEngine(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_daily_compliance_cycle(self):
        cycle = self.engine.run_daily_compliance_cycle()
        self.assertEqual(cycle["status"], "COMPLETED")
        self.assertEqual(cycle["total_entities_scanned"], 6)
        self.assertEqual(cycle["pending_filings_count"], 6)
        self.assertTrue(len(cycle["pending_filings"]) > 0)


if __name__ == "__main__":
    unittest.main()
