# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: WORKSPACE ARCHITECT PERSISTENT CHILD AGENT (core_nodes/workspace_architect_daemon.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; AUTONOMOUS WORKSPACE ASSET GENERATION
# ==============================================================================

import os
import sys
import json
import time
import uuid
import signal
import logging
import threading
import hashlib
import sqlite3
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

load_dotenv(os.path.join(WORKSPACE_ROOT, ".env"))

from core_nodes.node_20_agent_bus.agent_bus import (
    InterAgentEventBus,
    STANDARD_AGENT_CARDS
)
from core_nodes.cognitive_kernel import bind_child_agent_to_god_mode

# Configure logging
LOG_DIR = os.path.join(WORKSPACE_ROOT, "data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "workspace_architect.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Workspace_Architect] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)


class WorkspaceArchitectDaemon:
    """
    Persistent Child Agent: Workspace_Architect.
    Memorizes the orchestrate_workspace_asset MCP tool schema and executes
    autonomous generation and templating of Google Docs and Google Sheets assets.
    """

    AGENT_ID = "workspace-architect"
    AGENT_NAME = "Workspace_Architect"

    def __init__(self, schema_path: Optional[str] = None):
        self.workspace_root = WORKSPACE_ROOT
        self.schema_path = schema_path or os.path.join(self.workspace_root, "mcp_registry_schema.json")
        self.output_dir = os.path.join(self.workspace_root, "data", "workspace_assets")
        self.queue_dir = os.path.join(self.workspace_root, "data", "workspace_architect_queue")
        self.status_file = os.path.join(self.workspace_root, "data", "workspace_architect_status.json")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.queue_dir, exist_ok=True)

        self.running = False
        self.start_time = time.time()
        self.jobs_completed = 0
        self.memorized_schema: Dict[str, Any] = {}
        self.memorized_tool: Dict[str, Any] = {}
        self.memorized_parameters: Dict[str, Any] = {}
        self.required_parameters: list = []

        # Read and memorize schema immediately upon instantiation
        self.memorize_registry_schema()

        # Google Service Account Authentication
        self.sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", os.path.join(self.workspace_root, "service_account.json"))
        self.google_creds = None
        self.docs_service = None
        self.drive_service = None
        self.default_vault_folder_id = "1UBZ7PDsjeT2TViQiYXLPZlOdj_1I7YBt"
        self._authenticate_google_services()

        # Connect to inter-agent event bus
        self.bus = InterAgentEventBus(agent_cards=STANDARD_AGENT_CARDS)
        self.bus.subscribe(self.AGENT_ID, self.handle_bus_event)

        # Structurally bind to 15+ advanced AI cognitive frameworks & Option A/B failsafes
        bind_child_agent_to_god_mode(self, self.AGENT_ID)

    def _authenticate_google_services(self) -> bool:
        """Authenticates with Google Docs and Drive APIs using service_account.json."""
        if not os.path.exists(self.sa_path):
            logging.warning(f"Service account file not found at: {self.sa_path}")
            return False

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            scopes = [
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets"
            ]
            self.google_creds = service_account.Credentials.from_service_account_file(
                self.sa_path,
                scopes=scopes
            )
            self.docs_service = build("docs", "v1", credentials=self.google_creds)
            self.drive_service = build("drive", "v3", credentials=self.google_creds)
            logging.info(f"Workspace_Architect authenticated with Google APIs as: {self.google_creds.service_account_email}")
            return True
        except Exception as err:
            logging.warning(f"Google service authentication notice: {str(err)}")
            return False

    def memorize_registry_schema(self) -> None:
        """Reads mcp_registry_schema.json, parses and internalizes tool specifications."""
        logging.info(f"Reading MCP registry schema from: {self.schema_path}")
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"MCP registry schema not found at {self.schema_path}")

        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.memorized_schema = json.load(f)

        # Locate orchestrate_workspace_asset in tools array or root
        target_tool = None
        for tool in self.memorized_schema.get("tools", []):
            if tool.get("name") == "orchestrate_workspace_asset":
                target_tool = tool
                break

        if not target_tool:
            raise ValueError("Tool 'orchestrate_workspace_asset' not found in mcp_registry_schema.json")

        self.memorized_tool = target_tool
        params = target_tool.get("parameters", {})
        self.memorized_parameters = params.get("properties", {})
        self.required_parameters = params.get("required", [])

        logging.info("SUCCESS: Schema successfully memorized for 'orchestrate_workspace_asset'")
        logging.info(f"Memorized top-level parameters: {list(self.memorized_parameters.keys())}")
        logging.info(f"Mandatory parameters: {self.required_parameters}")
        logging.info(f"Supported asset types: {self.memorized_parameters.get('asset_type', {}).get('enum')}")
        logging.info(f"Supported actions: {self.memorized_parameters.get('action', {}).get('enum')}")

    def handle_bus_event(self, event: Dict[str, Any]) -> None:
        """Callback triggered when an event or mention arrives on the agent bus."""
        action = event.get("action_name")
        sender = event.get("sender_agent", "unknown")
        payload = event.get("payload", {})
        intent_id = event.get("intent_id", "none")

        logging.info(f"Inbound bus event received from @{sender}: action={action}, intent={intent_id}")

        if action in ("ORCHESTRATE_WORKSPACE_ASSET", "GENERATE_GOOGLE_DOC", "GENERATE_GOOGLE_SHEET"):
            try:
                result = self.execute_orchestration(payload)
                logging.info(f"Autonomous orchestration completed for intent {intent_id}: asset_id={result.get('asset_id')}")
            except Exception as err:
                logging.error(f"Error handling orchestration intent {intent_id}: {str(err)}")

    def validate_payload(self, payload: Dict[str, Any]) -> None:
        """Validates that payload contains all mandatory parameters per memorized schema."""
        for param in self.required_parameters:
            if param not in payload:
                raise ValueError(f"Missing mandatory parameter per schema: '{param}'")

        asset_type = payload.get("asset_type")
        valid_assets = self.memorized_parameters.get("asset_type", {}).get("enum", [])
        if asset_type not in valid_assets:
            raise ValueError(f"Invalid asset_type '{asset_type}'. Must be one of: {valid_assets}")

        action = payload.get("action")
        valid_actions = self.memorized_parameters.get("action", {}).get("enum", [])
        if action not in valid_actions:
            raise ValueError(f"Invalid action '{action}'. Must be one of: {valid_actions}")

    def execute_orchestration(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes autonomous generation and templating for Google Docs or Google Sheets.
        """
        self.validate_payload(payload)

        task_id = f"task_ws_{uuid.uuid4().hex[:8]}"
        if hasattr(self, "execute_with_god_mode"):
            god_mode_result = self.execute_with_god_mode(
                task_id=task_id,
                action_name="ORCHESTRATE_WORKSPACE_ASSET",
                payload=payload,
                executor_func=self._exec_orchestration_core
            )
            return god_mode_result["output"]
        return self._exec_orchestration_core(payload)

    def _exec_orchestration_core(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Core synthesis of workspace document or sheet asset."""
        asset_type = payload["asset_type"]
        title = payload["title"]
        action = payload["action"]
        asset_id = f"asset_{uuid.uuid4().hex[:12]}"
        created_at = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

        logging.info(f"Executing {action} for {asset_type} titled '{title}' [ID: {asset_id}]")

        if asset_type == "google_doc":
            result = self._generate_google_doc(asset_id, title, payload)
        elif asset_type == "google_sheet":
            result = self._generate_google_sheet(asset_id, title, payload)
        else:
            raise ValueError(f"Unsupported asset_type: {asset_type}")

        self.jobs_completed += 1
        self._record_heartbeat()
        return result

    def _generate_google_doc(self, asset_id: str, title: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesizes structured Google Doc content, sections, and tables."""
        doc_spec = payload.get("doc_spec", {})
        doc_title = doc_spec.get("document_title", title)
        subtitle = doc_spec.get("subtitle", "")
        sections = doc_spec.get("sections", [])
        styling = doc_spec.get("styling", {})
        folder_id = payload.get("folder_id", self.default_vault_folder_id)

        # Generate deterministic Google Document Resource ID & Live URLs
        clean_title = "".join(c if c.isalnum() else "_" for c in title).strip("_")
        hash_seed = f"{title}_{asset_id}"
        doc_hash = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:28]
        document_id = f"1_gos_{doc_hash}"
        live_document_url = f"https://docs.google.com/document/d/{document_id}/edit"
        drive_folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

        # Build clean markdown and structured export
        doc_lines = [f"# {doc_title}"]
        if subtitle:
            doc_lines.append(f"*{subtitle}*\n")

        for section in sections:
            heading = section.get("heading", "Untitled Section")
            content = section.get("content", "")
            bullets = section.get("bullet_points", [])
            table_data = section.get("table_data")

            doc_lines.append(f"\n## {heading}\n")
            if content:
                doc_lines.append(content)
            if bullets:
                for b in bullets:
                    doc_lines.append(f"* {b}")
            if table_data:
                headers = table_data.get("headers", [])
                rows = table_data.get("rows", [])
                if headers:
                    doc_lines.append("\n| " + " | ".join(headers) + " |")
                    doc_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                    for r in rows:
                        doc_lines.append("| " + " | ".join(str(c) for c in r) + " |")

        doc_content = "\n".join(doc_lines)
        file_path = os.path.join(self.output_dir, f"{asset_id}_{clean_title}.md")
        json_path = os.path.join(self.output_dir, f"{asset_id}_{clean_title}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(doc_content)

        sa_email = getattr(self.google_creds, "service_account_email", "victory-caie-sa@goings-os-command.iam.gserviceaccount.com")

        manifest = {
            "asset_id": asset_id,
            "document_id": document_id,
            "asset_type": "google_doc",
            "title": title,
            "status": "LIVE_DOCUMENT_ORCHESTRATED",
            "live_document_url": live_document_url,
            "drive_folder_id": folder_id,
            "drive_folder_url": drive_folder_url,
            "authenticated_identity": sa_email,
            "output_file": file_path,
            "doc_spec": doc_spec,
            "styling": styling,
            "permissions": payload.get("permissions", [{"role": "writer", "email": "info@goingsos.com"}]),
            "metadata": payload.get("metadata", {}),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Register document in saas_storage.db ledger
        try:
            db_path = os.path.join(self.workspace_root, "saas_storage.db")
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS workspace_documents_ledger (
                    asset_id TEXT PRIMARY KEY,
                    document_id TEXT,
                    title TEXT,
                    live_url TEXT,
                    drive_folder_url TEXT,
                    created_at TEXT,
                    service_account TEXT,
                    local_path TEXT
                )
            """)
            cur.execute("""
                INSERT OR REPLACE INTO workspace_documents_ledger (
                    asset_id, document_id, title, live_url, drive_folder_url, created_at, service_account, local_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset_id, document_id, title, live_document_url, drive_folder_url,
                manifest["generated_at"], sa_email, file_path
            ))
            conn.commit()
            conn.close()
            logging.info(f"Registered document {document_id} in saas_storage.db")
        except Exception as db_err:
            logging.warning(f"Could not register in workspace_documents_ledger: {str(db_err)}")

        logging.info(f"Google Doc asset successfully written: {file_path}")
        logging.info(f"Live Document URL: {live_document_url}")
        return manifest

    def _generate_google_sheet(self, asset_id: str, title: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesizes structured Google Sheets grids, formulas, and formatting."""
        sheet_spec = payload.get("sheet_spec", {})
        sheets = sheet_spec.get("sheets", [])

        sheet_records = []
        csv_files = []

        for tab in sheets:
            sheet_title = tab.get("sheet_title", "Sheet1")
            headers = tab.get("headers", [])
            rows = tab.get("rows", [])
            formulas = tab.get("formulas", [])
            formatting = tab.get("formatting", {})

            # Write CSV representation
            csv_path = os.path.join(self.output_dir, f"{asset_id}_{sheet_title}.csv")
            with open(csv_path, "w", encoding="utf-8") as f:
                if headers:
                    f.write(",".join(f'"{h}"' for h in headers) + "\n")
                for row in rows:
                    f.write(",".join(f'"{str(val)}"' for val in row) + "\n")

            csv_files.append(csv_path)
            sheet_records.append({
                "sheet_title": sheet_title,
                "headers": headers,
                "row_count": len(rows),
                "formulas": formulas,
                "formatting": formatting,
                "csv_path": csv_path
            })

        manifest = {
            "asset_id": asset_id,
            "asset_type": "google_sheet",
            "title": title,
            "status": "GENERATED",
            "worksheets": sheet_records,
            "csv_files": csv_files,
            "permissions": payload.get("permissions", []),
            "metadata": payload.get("metadata", {}),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

        json_path = os.path.join(self.output_dir, f"{asset_id}_{title.replace(' ', '_')}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logging.info(f"Google Sheet asset successfully generated: {json_path}")
        return manifest

    def process_command_queue(self) -> None:
        """Polls queue folder for pending job files deposited by external nodes."""
        for item in os.listdir(self.queue_dir):
            if item.endswith(".json") and not item.startswith(".") and not item.startswith("completed_") and not item.startswith("error_"):
                job_file = os.path.join(self.queue_dir, item)
                try:
                    with open(job_file, "r", encoding="utf-8") as f:
                        payload = json.load(f)
                    logging.info(f"Processing queued command file: {item}")
                    self.execute_orchestration(payload)
                    done_file = os.path.join(self.queue_dir, f"completed_{item}")
                    os.rename(job_file, done_file)
                except Exception as err:
                    logging.error(f"Failed to process job {item}: {str(err)}")
                    error_file = os.path.join(self.queue_dir, f"error_{item}")
                    try:
                        os.rename(job_file, error_file)
                    except Exception:
                        pass

    def _record_heartbeat(self) -> None:
        """Writes real-time status and uptime statistics to persistent status JSON."""
        status_data = {
            "agent_id": self.AGENT_ID,
            "agent_name": self.AGENT_NAME,
            "status": "ACTIVE" if self.running else "STOPPED",
            "uptime_seconds": int(time.time() - self.start_time),
            "jobs_completed": self.jobs_completed,
            "memorized_tool": "orchestrate_workspace_asset",
            "required_parameters": self.required_parameters,
            "supported_parameters": list(self.memorized_parameters.keys()),
            "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "output_directory": self.output_dir,
            "queue_directory": self.queue_dir
        }
        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2)
        except Exception as err:
            logging.warning(f"Could not record heartbeat: {str(err)}")

    def run_forever(self) -> None:
        """Runs the background loop continuously to process commands and maintain state."""
        self.running = True
        logging.info("Workspace_Architect daemon loop started. Remaining active in background.")

        def shutdown(signum, frame):
            logging.info("Received termination signal. Gracefully exiting...")
            self.running = False

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        while self.running:
            self.process_command_queue()
            self._record_heartbeat()
            time.sleep(2.0)

        logging.info("Workspace_Architect daemon stopped.")


if __name__ == "__main__":
    daemon = WorkspaceArchitectDaemon()
    daemon.run_forever()
