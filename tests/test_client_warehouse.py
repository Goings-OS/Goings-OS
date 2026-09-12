# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UNIT TESTS FOR CLIENT WAREHOUSE ENGINE (tests/test_client_warehouse.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; UNITTEST ALIGNED
# ==============================================================================

import os
import sys
import shutil
import tempfile
import sqlite3
import unittest
from unittest.mock import MagicMock

# Ensure workspace root is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from node_08_vault import (
    ClientWarehouseEngine,
    STANDARD_CLIENT_SUBFOLDERS,
    STATUTORY_CITATIONS
)


class TestClientWarehouseEngine(unittest.TestCase):
    """Unit test suite verifying Google Drive provisioning, compliance stamping, and Sheets sync."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.saas_db = os.path.join(self.temp_dir, "test_saas_storage.db")
        self.engine = ClientWarehouseEngine(
            base_dir=self.temp_dir,
            saas_db_path=self.saas_db,
            enable_live_google_apis=False
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_database_initialization(self):
        """Verifies tables are created in saas_storage.db with WAL mode."""
        conn = sqlite3.connect(self.saas_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        conn.close()

        self.assertIn("compliance_stamps", tables)
        self.assertIn("client_warehouse_folders", tables)
        self.assertIn("sheets_sync_history", tables)

    def test_provision_client_folder_hierarchy(self):
        """Verifies automated creation of the 5 standardized Google Drive subfolders."""
        client_id = "CLI_KIG_9001"
        client_name = "Marcus Vance Enterprises"

        folders_meta = self.engine.provision_client_folder_hierarchy(
            client_id=client_id,
            client_name=client_name
        )

        self.assertEqual(folders_meta["client_id"], client_id)
        self.assertEqual(folders_meta["client_name"], client_name)
        self.assertTrue(folders_meta["root_folder_id"].startswith("gdrive_folder_"))
        self.assertTrue(folders_meta["root_folder_url"].startswith("https://drive.google.com/drive/folders/"))

        # Verify all 5 subfolders exist
        subfolders = folders_meta["subfolders"]
        self.assertEqual(len(subfolders), 5)
        for expected_sub in STANDARD_CLIENT_SUBFOLDERS:
            self.assertIn(expected_sub, subfolders)
            self.assertTrue(subfolders[expected_sub]["folder_url"].startswith("https://drive.google.com/drive/folders/"))

        # Verify record in saas_storage.db
        conn = sqlite3.connect(self.saas_db)
        cursor = conn.cursor()
        cursor.execute("SELECT client_id, client_name, intake_folder_url FROM client_warehouse_folders WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], client_id)
        self.assertEqual(row[1], client_name)
        self.assertEqual(row[2], subfolders["Intake"]["folder_url"])

    def test_stamp_compliance_record(self):
        """Verifies immutable compliance stamping with SHA-256 hash, operator ID, and ISO-8601 timestamp."""
        client_id = "CLI_TBE_7701"
        doc_name = "Experian_Forensic_Audit_Report.pdf"
        doc_content = b"EVIDENCE_RECORD_CREDIT_BUREAU_DISPUTE_ROUND_01_PROCEEDING"
        operator_id = "OP_SEC_007"
        citation = STATUTORY_CITATIONS["FCRA_INVESTIGATION"]

        stamp_result = self.engine.stamp_compliance_record(
            client_id=client_id,
            document_name=doc_name,
            document_content=doc_content,
            operator_id=operator_id,
            statutory_citation=citation,
            folder_category="Forensic Audits",
            metadata={"dispute_round": 1, "target_bureau": "EXPERIAN"}
        )

        self.assertTrue(stamp_result["stamp_id"].startswith("STAMP_CLI_TBE_7701"))
        self.assertEqual(stamp_result["client_id"], client_id)
        self.assertEqual(stamp_result["operator_id"], operator_id)
        self.assertEqual(stamp_result["statutory_citation"], citation)
        self.assertEqual(len(stamp_result["sha256_hash"]), 64)
        self.assertEqual(len(stamp_result["verification_signature"]), 64)
        self.assertEqual(stamp_result["status"], "IMMUTABLY_RECORDED")

        # Verify timestamp contains UTC timezone notation
        self.assertTrue("+" in stamp_result["timestamp_iso"] or "Z" in stamp_result["timestamp_iso"])

        # Check retrieval from database
        stamps = self.engine.get_compliance_stamps(client_id)
        self.assertEqual(len(stamps), 1)
        self.assertEqual(stamps[0]["document_name"], doc_name)
        self.assertEqual(stamps[0]["operator_id"], operator_id)

    def test_verify_compliance_stamp(self):
        """Verifies tamper detection in compliance stamping utility."""
        client_id = "CLI_VERIFY_101"
        original_doc = b"GENUINE_FCRA_BUREAU_RESPONSE_DOCUMENT"
        tampered_doc = b"ALTERED_OR_TAMPERED_DOCUMENT_BYTES"

        stamp = self.engine.stamp_compliance_record(
            client_id=client_id,
            document_name="Bureau_Letter.pdf",
            document_content=original_doc,
            operator_id="OP_LEGAL_99"
        )
        stamp_id = stamp["stamp_id"]

        # 1. Verification of genuine doc must pass
        self.assertTrue(self.engine.verify_compliance_stamp(stamp_id, original_doc))

        # 2. Verification of tampered doc must fail
        self.assertFalse(self.engine.verify_compliance_stamp(stamp_id, tampered_doc))

    def test_sync_client_to_sheets_offline_buffer(self):
        """Verifies Google Sheets sync formatting and database audit trail in offline fallback mode."""
        client_record = {
            "client_id": "CLI_SHEETS_404",
            "client_name": "Titanium Logistics LLC",
            "status": "DISPUTES_ACTIVE",
            "intake_folder_url": "https://drive.google.com/drive/folders/intake_url",
            "forensic_audits_url": "https://drive.google.com/drive/folders/audits_url",
            "dispute_rounds_url": "https://drive.google.com/drive/folders/disputes_url",
            "furnisher_responses_url": "https://drive.google.com/drive/folders/furnisher_url",
            "compliance_evidence_url": "https://drive.google.com/drive/folders/evidence_url",
            "latest_compliance_stamp": "STAMP_001_ABC",
            "statutory_citation": STATUTORY_CITATIONS["CROA_COMPLIANCE"]
        }

        spreadsheet_id = "1MockSpreadsheetIdForGoingsOSClients"
        sync_result = self.engine.sync_client_to_sheets(
            spreadsheet_id=spreadsheet_id,
            client_record=client_record
        )

        self.assertEqual(sync_result["sync_status"], "SHEETS_OFFLINE_BUFFERED")
        self.assertEqual(sync_result["client_id"], "CLI_SHEETS_404")
        self.assertEqual(len(sync_result["row_values"]), 11)
        self.assertEqual(sync_result["row_values"][0], "CLI_SHEETS_404")
        self.assertEqual(sync_result["row_values"][1], "Titanium Logistics LLC")

        # Verify audit log in saas_storage.db
        conn = sqlite3.connect(self.saas_db)
        cursor = conn.cursor()
        cursor.execute("SELECT sync_id, client_id, sync_status FROM sheets_sync_history WHERE client_id = ?", ("CLI_SHEETS_404",))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[1], "CLI_SHEETS_404")
        self.assertEqual(row[2], "SHEETS_OFFLINE_BUFFERED")

    def test_sync_client_to_sheets_with_mock_service(self):
        """Verifies Google Sheets API append invocation when sheets_service is live."""
        mock_sheets = MagicMock()
        mock_values = MagicMock()
        mock_append = MagicMock()
        mock_sheets.spreadsheets.return_value.values.return_value = mock_values
        mock_values.append.return_value = mock_append
        mock_append.execute.return_value = {"updates": {"updatedRows": 1}}

        self.engine.sheets_service = mock_sheets

        client_record = {
            "client_id": "CLI_SHEETS_LIVE",
            "client_name": "Live Client Corp",
            "status": "PROCESSED",
            "intake_folder_url": "url1",
            "forensic_audits_url": "url2",
            "dispute_rounds_url": "url3",
            "furnisher_responses_url": "url4",
            "compliance_evidence_url": "url5",
            "latest_compliance_stamp": "STAMP_LIVE",
            "statutory_citation": STATUTORY_CITATIONS["GLBA_PRIVACY"]
        }

        sync_result = self.engine.sync_client_to_sheets(
            spreadsheet_id="test_sheet_123",
            client_record=client_record
        )

        self.assertEqual(sync_result["sync_status"], "SHEETS_LIVE_APPENDED")
        mock_values.append.assert_called_once()

    def test_onboard_client_end_to_end(self):
        """Verifies end-to-end client warehousing onboarding coordinating folders, stamping, and sheets."""
        initial_docs = [
            {
                "name": "Client_Agreement_Signed.pdf",
                "content": b"SIGNED_CROA_DISCLOSURE_AND_POWER_OF_ATTORNEY",
                "category": "Intake",
                "statutory_citation": STATUTORY_CITATIONS["CROA_COMPLIANCE"]
            },
            {
                "name": "Credit_Report_Forensic_Extraction.json",
                "content": b'{"negative_items": 4, "inaccuracies_flagged": 3}',
                "category": "Forensic Audits",
                "statutory_citation": STATUTORY_CITATIONS["FCRA_DISCLOSURE"]
            }
        ]

        onboard_res = self.engine.onboard_client(
            client_id="CLI_E2E_888",
            client_name="E2E Global Logistics",
            operator_id="OP_DIRECTOR_01",
            initial_documents=initial_docs,
            spreadsheet_id="1SpreadsheetE2ETest"
        )

        self.assertEqual(onboard_res["status"], "SUCCESS_ONBOARDED")
        self.assertEqual(onboard_res["client_id"], "CLI_E2E_888")
        self.assertEqual(len(onboard_res["folders"]["subfolders"]), 5)
        self.assertEqual(len(onboard_res["compliance_stamps"]), 2)
        self.assertIsNotNone(onboard_res["sheets_sync"])

    def test_provision_with_parent_folder_id_mock_drive(self):
        """Verifies files().create sets parents metadata and supportsAllDrives for root and subfolders."""
        mock_drive = MagicMock()
        mock_files = MagicMock()
        mock_create = MagicMock()
        mock_drive.files.return_value = mock_files
        mock_files.create.return_value = mock_create

        # Mock folder returns
        created_folders = [
            {"id": "root_mock_id", "webViewLink": "https://drive.google.com/drive/folders/root_mock_id"},
            {"id": "sub_1", "webViewLink": "https://drive.google.com/drive/folders/sub_1"},
            {"id": "sub_2", "webViewLink": "https://drive.google.com/drive/folders/sub_2"},
            {"id": "sub_3", "webViewLink": "https://drive.google.com/drive/folders/sub_3"},
            {"id": "sub_4", "webViewLink": "https://drive.google.com/drive/folders/sub_4"},
            {"id": "sub_5", "webViewLink": "https://drive.google.com/drive/folders/sub_5"},
        ]
        mock_create.execute.side_effect = created_folders

        self.engine.drive_service = mock_drive

        parent_id = "parent_folder_test_999"
        res = self.engine.provision_client_folder_hierarchy(
            client_id="CLI_PARENT_001",
            client_name="Parent Test Client",
            parent_folder_id=parent_id
        )

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["root_folder_id"], "root_mock_id")
        self.assertEqual(res["storage_mode"], "GCS_DRIVE_LIVE")
        self.assertEqual(mock_files.create.call_count, 6)

        # First call is root folder creation: parents must be [parent_id]
        first_call_kwargs = mock_files.create.call_args_list[0].kwargs
        self.assertEqual(first_call_kwargs["body"]["parents"], [parent_id])
        self.assertTrue(first_call_kwargs.get("supportsAllDrives"))

        # Subsequent calls are the 5 subfolders: parents must be [root_mock_id]
        for sub_call in mock_files.create.call_args_list[1:]:
            kwargs = sub_call.kwargs
            self.assertEqual(kwargs["body"]["parents"], ["root_mock_id"])
            self.assertTrue(kwargs.get("supportsAllDrives"))

    def test_onboard_client_passes_parent_folder_id(self):
        """Verifies onboard_client accepts parent_folder_id and forwards it to provisioner."""
        mock_drive = MagicMock()
        mock_files = MagicMock()
        mock_create = MagicMock()
        mock_drive.files.return_value = mock_files
        mock_files.create.return_value = mock_create

        created_folders = [
            {"id": "root_onboard_id", "webViewLink": "https://drive.google.com/drive/folders/root_onboard_id"},
            {"id": "sub_1", "webViewLink": "https://drive.google.com/drive/folders/sub_1"},
            {"id": "sub_2", "webViewLink": "https://drive.google.com/drive/folders/sub_2"},
            {"id": "sub_3", "webViewLink": "https://drive.google.com/drive/folders/sub_3"},
            {"id": "sub_4", "webViewLink": "https://drive.google.com/drive/folders/sub_4"},
            {"id": "sub_5", "webViewLink": "https://drive.google.com/drive/folders/sub_5"},
        ]
        mock_create.execute.side_effect = created_folders
        self.engine.drive_service = mock_drive

        target_parent = "target_parent_drive_folder_id"
        res = self.engine.onboard_client(
            client_id="CLI_FWD_777",
            client_name="Forward Parent LLC",
            operator_id="OP_VAL_01",
            parent_folder_id=target_parent
        )

        self.assertEqual(res["status"], "SUCCESS_ONBOARDED")
        first_call_kwargs = mock_files.create.call_args_list[0].kwargs
        self.assertEqual(first_call_kwargs["body"]["parents"], [target_parent])

    def test_live_drive_failure_returns_failed_auth(self):
        """Verifies live Google Drive API creation failure returns FAILED_AUTH without fake URLs."""
        mock_drive = MagicMock()
        mock_files = MagicMock()
        mock_drive.files.return_value = mock_files
        mock_files.create.side_effect = Exception("Google Drive API 403: The caller does not have permission")

        self.engine.drive_service = mock_drive

        # 1. Direct call to provision_client_folder_hierarchy
        prov_res = self.engine.provision_client_folder_hierarchy(
            client_id="CLI_FAIL_001",
            client_name="Failing Client Corp",
            parent_folder_id="parent_123"
        )
        self.assertEqual(prov_res["status"], "FAILED_AUTH")
        self.assertIn("The caller does not have permission", prov_res["error"])
        self.assertNotIn("https://drive.google.com/drive/folders/gdrive_folder_", prov_res.get("root_folder_url", ""))

        # 2. onboard_client wrapping failure
        onboard_res = self.engine.onboard_client(
            client_id="CLI_FAIL_002",
            client_name="Failing Client Corp 2",
            operator_id="OP_FAIL",
            parent_folder_id="parent_123"
        )
        self.assertEqual(onboard_res["status"], "FAILED_AUTH")
        self.assertIn("The caller does not have permission", onboard_res["error"])

    def test_mcp_gateway_routes_integrity(self):
        """Verifies mounting ClientWarehouseEngine preserves active MCP Ingress Gateway routes."""
        import ingress_gateway
        routes = [r.path for r in ingress_gateway.app.routes]
        self.assertIn("/mcp", routes)
        self.assertIn("/health", routes)
        self.assertIn("/credit", routes)
        self.assertIn("/spotlight", routes)


if __name__ == "__main__":
    unittest.main()

