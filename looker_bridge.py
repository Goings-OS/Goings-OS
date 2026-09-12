# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: LOOKER STUDIO CLOUD BRIDGE PROTOCOL
# COMPLIANCE: ZERO EM-DASHES; SILENT DAEMON EXECUTION
# ==============================================================================

import os
import sys
import time
import json
import sqlite3
import argparse

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

# --- PRODUCTION LIVE GOOGLE BIGQUERY IMPORTS ---
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_SDK_AVAILABLE = True
except ImportError:
    BIGQUERY_SDK_AVAILABLE = False

from core_nodes.node_08_vault.schema_manager import SchemaManager, DatabaseObservabilityAgent

class LookerStudioBridge:
    """Bridges local SQLite memory tables to Google BigQuery for Looker Studio ingestion."""

    def __init__(self):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.root_dir, "goings_os_vault.db")
        self.humanitarian_db = os.path.join(self.root_dir, "choice_legacy_vault.db")
        self.log_path = os.path.join(self.root_dir, "looker_bridge.log")
        self.dataset_name = "looker_studio_sync"
        
        # Ingest AI-native schema interpretation and observability agent patterns
        instructions_path = os.path.join(self.root_dir, "instructions.md")
        self.schema_manager = SchemaManager(self.db_path, instructions_path)
        self.observability_agent = DatabaseObservabilityAgent(self.db_path, self.schema_manager)
        
        self._ensure_database_records()

    def log_sync(self, message: str):
        """Appends synchronization confirmations cleanly to looker_bridge.log without em-dashes."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        clean_msg = message.replace("\u2014", ": ").replace("--", ": ")
        log_line = f"[{timestamp}] {clean_msg}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(log_line)

    def _ensure_database_records(self):
        """Validates that local database tables and mock records exist for synchronization."""
        # 1. Initialize owners_draw_allocations in goings_os_vault.db if empty
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='owners_draw_allocations'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    CREATE TABLE owners_draw_allocations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        client_name TEXT,
                        form_name TEXT,
                        transaction_id TEXT UNIQUE,
                        allocated_amount REAL,
                        allocation_description TEXT
                    )
                """)
                conn.commit()

            cursor.execute("SELECT count(*) FROM owners_draw_allocations")
            if cursor.fetchone()[0] == 0:
                mock_draws = [
                    ("Terrence Goings", "Draw Request A", "TXN-80001", 1500.00, "Weekly shareholder draw allocation"),
                    ("Terrence Goings", "Draw Request B", "TXN-80002", 714.28, "Daily operational yield draw allocation"),
                    ("Tanita Brinkley", "Executive Draw C", "TXN-80003", 2500.00, "Corporate strategy partner draw allocation")
                ]
                cursor.executemany("""
                    INSERT OR IGNORE INTO owners_draw_allocations (timestamp, client_name, form_name, transaction_id, allocated_amount, allocation_description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [(time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), c, f, t, a, d) for c, f, t, a, d in mock_draws])
                conn.commit()
            conn.close()
        except sqlite3.Error as err:
            self.log_sync(f"SQLite error during commercial database setup: {str(err)}")

        # 2. Initialize classroom_student_telemetry in choice_legacy_vault.db if missing
        try:
            conn = sqlite3.connect(self.humanitarian_db, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='classroom_student_telemetry'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    CREATE TABLE classroom_student_telemetry (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        student_id TEXT UNIQUE,
                        student_name TEXT,
                        course_name TEXT,
                        attendance_score REAL,
                        grade_score REAL
                    )
                """)
                conn.commit()

            cursor.execute("SELECT count(*) FROM classroom_student_telemetry")
            if cursor.fetchone()[0] == 0:
                mock_students = [
                    ("STU-101", "Avery Brooks", "Humanitarian Leadership", 94.5, 88.0),
                    ("STU-102", "Jordan Hayes", "Non-profit Management", 98.0, 92.5),
                    ("STU-103", "Morgan Vance", "Sovereign Asset Protection", 91.0, 85.0)
                ]
                cursor.executemany("""
                    INSERT OR IGNORE INTO classroom_student_telemetry (timestamp, student_id, student_name, course_name, attendance_score, grade_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [(time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), sid, name, course, att, grade) for sid, name, course, att, grade in mock_students])
                conn.commit()
            conn.close()
        except sqlite3.Error as err:
            self.log_sync(f"SQLite error during humanitarian database setup: {str(err)}")

    def extract_owners_draw_allocations(self) -> list:
        """Queries the owners draw allocations table records from the database."""
        records = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, client_name, form_name, transaction_id, allocated_amount, allocation_description FROM owners_draw_allocations")
            for row in cursor.fetchall():
                records.append(dict(row))
            conn.close()
        except sqlite3.Error as err:
            self.log_sync(f"Failed to query owners draw allocations: {str(err)}")
        return records

    def extract_classroom_student_telemetry(self) -> list:
        """Queries the classroom student telemetry table records from the database."""
        records = []
        try:
            conn = sqlite3.connect(self.humanitarian_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, student_id, student_name, course_name, attendance_score, grade_score FROM classroom_student_telemetry")
            for row in cursor.fetchall():
                records.append(dict(row))
            conn.close()
        except sqlite3.Error as err:
            self.log_sync(f"Failed to query classroom student telemetry: {str(err)}")
        return records

    def execute_cloud_synchronization(self) -> bool:
        """Executes extraction from databases and transmits the payloads to BigQuery."""
        self.log_sync("Initializing Looker Studio Cloud Bridge synchronization cycle")
        
        # Extract database health observability metrics
        metrics = self.observability_agent.get_observability_metrics()
        drift_detected = metrics["drift_status"].get("drift_detected", False)
        migration_health = "HEALTHY" if (metrics["integrity_pass"] and not drift_detected) else "DEGRADED"
        self.log_sync(f"Migration Health Status: {migration_health} (Integrity Pass: {metrics['integrity_pass']}, Schema Drift: {drift_detected})")
        
        draws = self.extract_owners_draw_allocations()
        students = self.extract_classroom_student_telemetry()
        
        self.log_sync(f"Extraction complete: retrieved {len(draws)} owners draw records and {len(students)} student telemetry records")

        if BIGQUERY_SDK_AVAILABLE:
            try:
                client = bigquery.Client()
                dataset_ref = f"{client.project}.{self.dataset_name}"
                
                # Verify or create target dataset
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"
                try:
                    client.get_dataset(dataset_ref)
                except Exception:
                    client.create_dataset(dataset, timeout=30.0)
                    self.log_sync(f"Created BigQuery dataset: {self.dataset_name}")

                # Sync owners_draw_allocations
                draw_schema = [
                    bigquery.SchemaField("id", "INTEGER"),
                    bigquery.SchemaField("timestamp", "STRING"),
                    bigquery.SchemaField("client_name", "STRING"),
                    bigquery.SchemaField("form_name", "STRING"),
                    bigquery.SchemaField("transaction_id", "STRING"),
                    bigquery.SchemaField("allocated_amount", "FLOAT"),
                    bigquery.SchemaField("allocation_description", "STRING")
                ]
                self._load_to_bigquery(client, dataset_ref, "owners_draw_allocations", draws, draw_schema)

                # Sync classroom_student_telemetry
                student_schema = [
                    bigquery.SchemaField("id", "INTEGER"),
                    bigquery.SchemaField("timestamp", "STRING"),
                    bigquery.SchemaField("student_id", "STRING"),
                    bigquery.SchemaField("student_name", "STRING"),
                    bigquery.SchemaField("course_name", "STRING"),
                    bigquery.SchemaField("attendance_score", "FLOAT"),
                    bigquery.SchemaField("grade_score", "FLOAT")
                ]
                self._load_to_bigquery(client, dataset_ref, "classroom_student_telemetry", students, student_schema)

                self.log_sync("Looker Studio Cloud Bridge sync completed successfully using native client")
                return True
            except Exception as cloud_err:
                self.log_sync(f"BigQuery upload fault: {str(cloud_err)}: transitioning to fallback log storage")
                self._simulate_upload(draws, students)
                return False
        else:
            self.log_sync("Native Google BigQuery SDK not loaded: executing local fallback simulation")
            self._simulate_upload(draws, students)
            return True

    def _load_to_bigquery(self, client, dataset_ref, table_name, records, schema):
        """Loads JSON records into Google BigQuery with WRITE TRUNCATE mode."""
        table_ref = f"{dataset_ref}.{table_name}"
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition="WRITE_TRUNCATE"
        )
        job = client.load_table_from_json(records, table_ref, job_config=job_config)
        job.result()
        self.log_sync(f"Uploaded {len(records)} rows to BigQuery table: {table_name}")

    def _simulate_upload(self, draws: list, students: list):
        """Simulates cloud database upload when client credentials or libraries are not present."""
        metrics = self.observability_agent.get_observability_metrics()
        drift_detected = metrics["drift_status"].get("drift_detected", False)
        migration_health = "HEALTHY" if (metrics["integrity_pass"] and not drift_detected) else "DEGRADED"
        self.log_sync("Simulated upload: Table: owners_draw_allocations: rows synced: " + str(len(draws)))
        self.log_sync("Simulated upload: Table: classroom_student_telemetry: rows synced: " + str(len(students)))
        self.log_sync(f"Simulated upload: Metric: Migration Health Status: {migration_health}")
        self.log_sync("Sync confirmation logged successfully under local fallback protocols")

def run_bridge_daemon(bridge, interval=60.0):
    """Executes the bridge sync loop in a silent background daemon."""
    bridge.log_sync("Starting Looker Studio Cloud Bridge daemon service")
    while True:
        try:
            bridge.execute_cloud_synchronization()
        except Exception as daemon_fault:
            bridge.log_sync(f"Daemon process exception caught: {str(daemon_fault)}")
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Goings OS Looker Studio Cloud Bridge")
    parser.add_argument("--once", action="store_true", help="Execute a single synchronization cycle and exit")
    parser.add_argument("--interval", type=float, default=60.0, help="Daemon sync interval in seconds")
    args = parser.parse_args()

    bridge = LookerStudioBridge()

    if args.once:
        print("Executing single-shot Looker Studio Cloud Bridge synchronization...")
        bridge.execute_cloud_synchronization()
        print("Sync execution cycle complete.")
    else:
        # Run silently in the background
        run_bridge_daemon(bridge, interval=args.interval)
