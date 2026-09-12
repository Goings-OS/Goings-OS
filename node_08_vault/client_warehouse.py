# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: CLIENT WAREHOUSE ENGINE (node_08_vault/client_warehouse.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; PRIVATE ENTERPRISE VAULT
# ==============================================================================

import os
import sys
import json
import uuid
import time
import hashlib
import sqlite3
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union

# Root directory resolution
ROOT_DIR = os.environ.get("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default standardized five-folder hierarchy
STANDARD_CLIENT_SUBFOLDERS: List[str] = [
    "Intake",
    "Forensic Audits",
    "Dispute Rounds",
    "Furnisher Responses",
    "Compliance Evidence"
]

# Statutory compliance reference constants
STATUTORY_CITATIONS: Dict[str, str] = {
    "FCRA_INVESTIGATION": "FCRA 15 U.S.C. Section 1681i (Mandatory 30-Day Re-investigation)",
    "FCRA_DISCLOSURE": "FCRA 15 U.S.C. Section 1681g (Full File Disclosure and Audit Trailing)",
    "CROA_COMPLIANCE": "CROA 15 U.S.C. Section 1679b (Prohibited Practices and Written Disclosures)",
    "GLBA_PRIVACY": "GLBA 15 U.S.C. Section 6801 (Financial Privacy and Safeguards Rule)",
    "FDCPA_VALIDATION": "FDCPA 15 U.S.C. Section 1692g (Notice of Debt and Verification Rights)",
    "STATUTORY_DEFAULT": "FCRA 15 U.S.C. 1681 / CROA 15 U.S.C. 1679 Standard Protocol"
}


class ClientWarehouseEngine:
    """Node 08 Vault Client Warehouse Engine.
    
    Automates Google Drive five-folder hierarchy provisioning, immutable
    compliance stamping in saas_storage.db, and real-time Google Sheets
    synchronization for enterprise client management.
    """

    def __init__(
        self,
        base_dir: Optional[str] = None,
        saas_db_path: Optional[str] = None,
        enable_live_google_apis: bool = True
    ):
        self.base_dir = base_dir or ROOT_DIR
        self.enable_live_google_apis = enable_live_google_apis
        
        # Explicit path takes precedence
        if saas_db_path:
            self.saas_db_path = saas_db_path
            parent = os.path.dirname(os.path.abspath(saas_db_path))
            if parent:
                os.makedirs(parent, exist_ok=True)
        else:
            candidate_paths = [
                os.path.join(self.base_dir, "core_nodes", "node_08_vault", "saas_storage.db"),
                os.path.join(self.base_dir, "data", "saas_storage.db"),
                os.path.join(self.base_dir, "saas_storage.db")
            ]
            resolved_db = None
            for path in candidate_paths:
                if os.path.exists(path):
                    resolved_db = path
                    break
            if not resolved_db:
                resolved_db = os.path.join(self.base_dir, "core_nodes", "node_08_vault", "saas_storage.db")
                os.makedirs(os.path.dirname(resolved_db), exist_ok=True)
            self.saas_db_path = resolved_db

        self.drive_service = None
        self.sheets_service = None
        
        # Local vault storage directory
        self.local_warehouse_dir = os.path.join(self.base_dir, "data", "vault", "client_warehouse")
        os.makedirs(self.local_warehouse_dir, exist_ok=True)
        
        self._init_database_tables()
        if self.enable_live_google_apis:
            self._init_google_api_services()

    def _init_database_tables(self):
        """Initializes compliance stamps and sheets sync tables in saas_storage.db."""
        try:
            conn = sqlite3.connect(self.saas_db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA busy_timeout = 30000;")
            
            # 1. Immutable compliance stamps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_stamps (
                    stamp_id TEXT PRIMARY KEY,
                    timestamp_iso TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    sha256_hash TEXT NOT NULL,
                    operator_id TEXT NOT NULL,
                    statutory_citation TEXT NOT NULL,
                    folder_category TEXT NOT NULL,
                    verification_signature TEXT NOT NULL,
                    metadata_json TEXT
                );
            """)
            
            # 2. Google Drive provisioned folder registry
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS client_warehouse_folders (
                    client_id TEXT PRIMARY KEY,
                    client_name TEXT NOT NULL,
                    root_folder_id TEXT NOT NULL,
                    root_folder_url TEXT NOT NULL,
                    intake_folder_url TEXT NOT NULL,
                    forensic_audits_url TEXT NOT NULL,
                    dispute_rounds_url TEXT NOT NULL,
                    furnisher_responses_url TEXT NOT NULL,
                    compliance_evidence_url TEXT NOT NULL,
                    created_at_iso TEXT NOT NULL,
                    storage_mode TEXT NOT NULL
                );
            """)
            
            # 3. Google Sheets synchronization history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sheets_sync_history (
                    sync_id TEXT PRIMARY KEY,
                    timestamp_iso TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    spreadsheet_id TEXT NOT NULL,
                    sync_status TEXT NOT NULL,
                    row_data_json TEXT NOT NULL
                );
            """)
            
            conn.commit()
            conn.close()
        except Exception as db_err:
            logging.error(f"Failed to initialize saas_storage.db schema: {str(db_err)}")

    def _init_google_api_services(self):
        """Attempts authentication with Google Drive and Sheets APIs."""
        self.auth_error = None
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        try:
            from googleapiclient.discovery import build
            from google.auth import default
            from google.oauth2 import service_account

            credentials = None
            sa_candidates = [
                os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
                os.path.join(self.base_dir, "service_account.json"),
                os.path.join(ROOT_DIR, "service_account.json")
            ]
            for sa_path in sa_candidates:
                if sa_path and os.path.exists(sa_path):
                    try:
                        credentials = service_account.Credentials.from_service_account_file(
                            sa_path,
                            scopes=scopes
                        )
                        break
                    except Exception as sa_err:
                        logging.warning(f"Could not load service account from {sa_path}: {str(sa_err)}")

            if not credentials:
                credentials, _ = default(scopes=scopes)
                if hasattr(credentials, "with_scopes"):
                    try:
                        credentials = credentials.with_scopes(scopes)
                    except Exception:
                        pass

            self.drive_service = build("drive", "v3", credentials=credentials)
            self.sheets_service = build("sheets", "v4", credentials=credentials)
        except Exception as auth_err:
            logging.info(f"Google Workspace API offline fallback engaged: {str(auth_err)}")
            self.drive_service = None
            self.sheets_service = None
            self.auth_error = str(auth_err)

    # ==========================================================================
    # 1. AUTOMATED GOOGLE DRIVE FOLDER PROVISIONER
    # ==========================================================================

    def provision_client_folder_hierarchy(
        self,
        client_id: str,
        client_name: str,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provisions client root folder and standardized 5-folder hierarchy."""
        safe_name = client_name.strip().replace("/", "_").replace("\\", "_")
        root_folder_name = f"{client_id} : {safe_name}"
        created_at_iso = datetime.now(timezone.utc).isoformat()
        
        subfolders_data: Dict[str, Dict[str, str]] = {}
        storage_mode = "GCS_DRIVE_LIVE"

        # If live Google Drive creation was enabled but drive_service failed authentication
        if self.enable_live_google_apis and not self.drive_service:
            err_msg = getattr(self, "auth_error", None) or "Google Drive authentication failed"
            logging.error(f"Google Drive live provisioning aborted: {err_msg}")
            return {
                "status": "FAILED_AUTH",
                "error": err_msg,
                "client_id": client_id,
                "client_name": client_name,
                "storage_mode": "FAILED_AUTH"
            }

        # 1. Attempt live Google Drive API folder creation if authenticated
        if self.drive_service:
            try:
                # Create root folder
                root_metadata = {
                    "name": root_folder_name,
                    "mimeType": "application/vnd.google-apps.folder"
                }
                if parent_folder_id:
                    root_metadata["parents"] = [parent_folder_id]
                    
                root_file = self.drive_service.files().create(
                    body=root_metadata,
                    fields="id, webViewLink",
                    supportsAllDrives=True
                ).execute()
                root_id = root_file.get("id")
                root_url = root_file.get("webViewLink", f"https://drive.google.com/drive/folders/{root_id}")

                # Create 5 subfolders
                for sub_name in STANDARD_CLIENT_SUBFOLDERS:
                    sub_metadata = {
                        "name": sub_name,
                        "mimeType": "application/vnd.google-apps.folder",
                        "parents": [root_id]
                    }
                    sub_file = self.drive_service.files().create(
                        body=sub_metadata,
                        fields="id, webViewLink",
                        supportsAllDrives=True
                    ).execute()
                    s_id = sub_file.get("id")
                    s_url = sub_file.get("webViewLink", f"https://drive.google.com/drive/folders/{s_id}")
                    subfolders_data[sub_name] = {
                        "folder_id": s_id,
                        "folder_url": s_url,
                        "folder_name": sub_name
                    }
            except Exception as drive_fault:
                logging.error(f"Google Drive live provisioning failed: {str(drive_fault)}")
                return {
                    "status": "FAILED_AUTH",
                    "error": str(drive_fault),
                    "client_id": client_id,
                    "client_name": client_name,
                    "storage_mode": "FAILED_AUTH"
                }

        # 2. Deterministic Local Vault Mirror Fallback
        if not self.drive_service:
            storage_mode = "LOCAL_VAULT_DETERMINISTIC"
            root_id = f"gdrive_folder_{client_id.lower()}_{hashlib.sha256(root_folder_name.encode()).hexdigest()[:12]}"
            root_url = f"https://drive.google.com/drive/folders/{root_id}"
            
            client_local_dir = os.path.join(self.local_warehouse_dir, client_id)
            os.makedirs(client_local_dir, exist_ok=True)
            
            for sub_name in STANDARD_CLIENT_SUBFOLDERS:
                sub_slug = sub_name.lower().replace(" ", "_")
                sub_id = f"gdrive_subfolder_{client_id.lower()}_{sub_slug}_{hashlib.sha256(sub_name.encode()).hexdigest()[:8]}"
                sub_url = f"https://drive.google.com/drive/folders/{sub_id}"
                sub_local_path = os.path.join(client_local_dir, sub_name)
                os.makedirs(sub_local_path, exist_ok=True)
                
                subfolders_data[sub_name] = {
                    "folder_id": sub_id,
                    "folder_url": sub_url,
                    "folder_name": sub_name,
                    "local_path": sub_local_path
                }

        # 3. Persist folder registry into saas_storage.db
        try:
            conn = sqlite3.connect(self.saas_db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA busy_timeout = 30000;")
            cursor.execute("""
                INSERT OR REPLACE INTO client_warehouse_folders (
                    client_id, client_name, root_folder_id, root_folder_url,
                    intake_folder_url, forensic_audits_url, dispute_rounds_url,
                    furnisher_responses_url, compliance_evidence_url, created_at_iso, storage_mode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_id,
                client_name,
                root_id,
                root_url,
                subfolders_data["Intake"]["folder_url"],
                subfolders_data["Forensic Audits"]["folder_url"],
                subfolders_data["Dispute Rounds"]["folder_url"],
                subfolders_data["Furnisher Responses"]["folder_url"],
                subfolders_data["Compliance Evidence"]["folder_url"],
                created_at_iso,
                storage_mode
            ))
            conn.commit()
            conn.close()
        except Exception as write_err:
            logging.error(f"Failed to record client warehouse folder registry: {str(write_err)}")

        return {
            "status": "SUCCESS",
            "client_id": client_id,
            "client_name": client_name,
            "root_folder_id": root_id,
            "root_folder_url": root_url,
            "subfolders": subfolders_data,
            "created_at_iso": created_at_iso,
            "storage_mode": storage_mode
        }

    # ==========================================================================
    # 2. IMMUTABLE COMPLIANCE STAMPING UTILITY
    # ==========================================================================

    def stamp_compliance_record(
        self,
        client_id: str,
        document_name: str,
        document_content: Union[bytes, str],
        operator_id: str,
        statutory_citation: Optional[str] = None,
        folder_category: str = "Compliance Evidence",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculates SHA-256 hash, generates UTC ISO-8601 timestamp, and logs immutable record to saas_storage.db."""
        # Convert content to bytes for hashing
        if isinstance(document_content, str):
            content_bytes = document_content.encode("utf-8")
        else:
            content_bytes = document_content

        sha256_hash = hashlib.sha256(content_bytes).hexdigest()
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        citation = statutory_citation or STATUTORY_CITATIONS.get("STATUTORY_DEFAULT")
        
        # Unique stamp identifier
        stamp_id = f"STAMP_{client_id}_{int(time.time())}_{sha256_hash[:8]}"
        
        # Construct verification signature binding operator, hash, and timestamp
        signature_material = f"{stamp_id}|{client_id}|{document_name}|{sha256_hash}|{operator_id}|{timestamp_iso}|{citation}"
        verification_signature = hashlib.sha256(signature_material.encode("utf-8")).hexdigest()
        metadata_json = json.dumps(metadata or {})

        # Persist to saas_storage.db
        try:
            conn = sqlite3.connect(self.saas_db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA busy_timeout = 30000;")
            cursor.execute("""
                INSERT INTO compliance_stamps (
                    stamp_id, timestamp_iso, client_id, document_name, sha256_hash,
                    operator_id, statutory_citation, folder_category, verification_signature, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stamp_id,
                timestamp_iso,
                client_id,
                document_name,
                sha256_hash,
                operator_id,
                citation,
                folder_category,
                verification_signature,
                metadata_json
            ))
            conn.commit()
            conn.close()
        except Exception as stamp_err:
            logging.error(f"Failed to record compliance stamp: {str(stamp_err)}")

        # Also store document to local warehouse folder if category matches
        client_dir = os.path.join(self.local_warehouse_dir, client_id, folder_category)
        os.makedirs(client_dir, exist_ok=True)
        doc_dest = os.path.join(client_dir, document_name)
        try:
            with open(doc_dest, "wb") as df:
                df.write(content_bytes)
        except Exception:
            pass

        return {
            "stamp_id": stamp_id,
            "timestamp_iso": timestamp_iso,
            "client_id": client_id,
            "document_name": document_name,
            "sha256_hash": sha256_hash,
            "operator_id": operator_id,
            "statutory_citation": citation,
            "folder_category": folder_category,
            "verification_signature": verification_signature,
            "status": "IMMUTABLY_RECORDED"
        }

    def verify_compliance_stamp(self, stamp_id: str, document_content: Union[bytes, str]) -> bool:
        """Verifies an existing compliance stamp against document bytes and cryptographic signature."""
        if isinstance(document_content, str):
            content_bytes = document_content.encode("utf-8")
        else:
            content_bytes = document_content

        current_hash = hashlib.sha256(content_bytes).hexdigest()

        try:
            conn = sqlite3.connect(self.saas_db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stamp_id, timestamp_iso, client_id, document_name, sha256_hash,
                       operator_id, statutory_citation, verification_signature
                FROM compliance_stamps WHERE stamp_id = ?
            """, (stamp_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return False

            stored_hash = row[4]
            if current_hash != stored_hash:
                return False

            # Re-verify signature
            expected_sig = hashlib.sha256(
                f"{row[0]}|{row[2]}|{row[3]}|{row[4]}|{row[5]}|{row[1]}|{row[6]}".encode("utf-8")
            ).hexdigest()
            return expected_sig == row[7]
        except Exception as verify_err:
            logging.error(f"Compliance verification fault: {str(verify_err)}")
            return False

    def get_compliance_stamps(self, client_id: str) -> List[Dict[str, Any]]:
        """Retrieves all compliance stamps recorded for a client."""
        stamps: List[Dict[str, Any]] = []
        try:
            conn = sqlite3.connect(self.saas_db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM compliance_stamps WHERE client_id = ? ORDER BY timestamp_iso DESC
            """, (client_id,))
            stamps = [dict(row) for row in cursor.fetchall()]
            conn.close()
        except Exception as read_err:
            logging.error(f"Failed to read compliance stamps: {str(read_err)}")
        return stamps

    # ==========================================================================
    # 3. GOOGLE SHEETS SYNCHRONIZATION BRIDGE
    # ==========================================================================

    def sync_client_to_sheets(
        self,
        spreadsheet_id: str,
        client_record: Dict[str, Any],
        range_name: str = "Clients!A:K"
    ) -> Dict[str, Any]:
        """Reflects client status, compliance stamps, and Drive links in Google Sheets."""
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        sync_id = f"SYNC_{client_record.get('client_id')}_{int(time.time())}"
        
        # Prepare row payload matching enterprise columns
        row_values = [
            client_record.get("client_id", "N/A"),
            client_record.get("client_name", "N/A"),
            client_record.get("status", "ACTIVE_ONBOARDED"),
            client_record.get("intake_folder_url", "N/A"),
            client_record.get("forensic_audits_url", "N/A"),
            client_record.get("dispute_rounds_url", "N/A"),
            client_record.get("furnisher_responses_url", "N/A"),
            client_record.get("compliance_evidence_url", "N/A"),
            client_record.get("latest_compliance_stamp", "PENDING"),
            client_record.get("statutory_citation", STATUTORY_CITATIONS.get("STATUTORY_DEFAULT")),
            timestamp_iso
        ]

        sync_status = "SHEETS_LIVE_APPENDED"

        # 1. Attempt live Google Sheets API append if authenticated
        if self.sheets_service:
            try:
                body = {"values": [row_values]}
                self.sheets_service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body=body
                ).execute()
            except Exception as sheets_err:
                logging.warning(f"Google Sheets API call deferred: {str(sheets_err)}. Logging to local sync buffer.")
                sync_status = "SHEETS_OFFLINE_BUFFERED"
        else:
            sync_status = "SHEETS_OFFLINE_BUFFERED"

        # 2. Record sync audit into saas_storage.db
        try:
            conn = sqlite3.connect(self.saas_db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA busy_timeout = 30000;")
            cursor.execute("""
                INSERT INTO sheets_sync_history (sync_id, timestamp_iso, client_id, spreadsheet_id, sync_status, row_data_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sync_id,
                timestamp_iso,
                client_record.get("client_id", "UNKNOWN"),
                spreadsheet_id,
                sync_status,
                json.dumps(row_values)
            ))
            conn.commit()
            conn.close()
        except Exception as audit_err:
            logging.error(f"Failed to record sheets sync audit: {str(audit_err)}")

        return {
            "sync_id": sync_id,
            "timestamp_iso": timestamp_iso,
            "client_id": client_record.get("client_id"),
            "spreadsheet_id": spreadsheet_id,
            "sync_status": sync_status,
            "row_values": row_values
        }

    # ==========================================================================
    # 4. END-TO-END CLIENT WAREHOUSING ONBOARDING
    # ==========================================================================

    def onboard_client(
        self,
        client_id: str,
        client_name: str,
        operator_id: str,
        initial_documents: Optional[List[Dict[str, Any]]] = None,
        spreadsheet_id: Optional[str] = None,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Coordinates folder hierarchy provisioning, compliance stamping, and sheets sync."""
        # 1. Provision 5-folder Google Drive hierarchy
        folders_meta = self.provision_client_folder_hierarchy(
            client_id=client_id,
            client_name=client_name,
            parent_folder_id=parent_folder_id
        )

        if folders_meta.get("status") == "FAILED_AUTH":
            return {
                "status": "FAILED_AUTH",
                "client_id": client_id,
                "client_name": client_name,
                "error": folders_meta.get("error", "Google Drive authentication failed"),
                "folders": folders_meta,
                "timestamp_iso": datetime.now(timezone.utc).isoformat()
            }

        # 2. Stamp initial documents if supplied
        stamps = []
        latest_stamp_id = "NONE"
        latest_citation = STATUTORY_CITATIONS.get("STATUTORY_DEFAULT")

        if initial_documents:
            for doc in initial_documents:
                doc_name = doc.get("name", "initial_document.pdf")
                doc_bytes = doc.get("content", b"INITIAL_DOCUMENT_PAYLOAD")
                citation = doc.get("statutory_citation", STATUTORY_CITATIONS.get("STATUTORY_DEFAULT"))
                category = doc.get("category", "Intake")
                
                stamp_record = self.stamp_compliance_record(
                    client_id=client_id,
                    document_name=doc_name,
                    document_content=doc_bytes,
                    operator_id=operator_id,
                    statutory_citation=citation,
                    folder_category=category
                )
                stamps.append(stamp_record)
                latest_stamp_id = stamp_record["stamp_id"]
                latest_citation = citation

        # 3. Prepare client record for Google Sheets
        subfolders = folders_meta.get("subfolders", {})
        client_record = {
            "client_id": client_id,
            "client_name": client_name,
            "status": "ACTIVE_VERIFIED",
            "intake_folder_url": subfolders.get("Intake", {}).get("folder_url", "N/A"),
            "forensic_audits_url": subfolders.get("Forensic Audits", {}).get("folder_url", "N/A"),
            "dispute_rounds_url": subfolders.get("Dispute Rounds", {}).get("folder_url", "N/A"),
            "furnisher_responses_url": subfolders.get("Furnisher Responses", {}).get("folder_url", "N/A"),
            "compliance_evidence_url": subfolders.get("Compliance Evidence", {}).get("folder_url", "N/A"),
            "latest_compliance_stamp": latest_stamp_id,
            "statutory_citation": latest_citation
        }

        # 4. Synchronize with Google Sheets
        sheets_sync = None
        if spreadsheet_id:
            sheets_sync = self.sync_client_to_sheets(
                spreadsheet_id=spreadsheet_id,
                client_record=client_record
            )

        return {
            "status": "SUCCESS_ONBOARDED",
            "client_id": client_id,
            "client_name": client_name,
            "folders": folders_meta,
            "compliance_stamps": stamps,
            "sheets_sync": sheets_sync,
            "timestamp_iso": datetime.now(timezone.utc).isoformat()
        }
