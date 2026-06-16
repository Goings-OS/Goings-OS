# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: HARDENED GARNET [SCOUT] B2B LEAD HARVESTING ENGINE (ENTERPRISE CORE)
# COMPLIANCE: ZERO EM-DASHES; WAL CONCURRENCY MATRIX; DYNAMIC ENVIRONMENT PATHS
# ==============================================================================

import logging
import os
import sqlite3
import sys
import time

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class GarnetScoutEngine:
    """Automates local B2B opportunity identification and infrastructure profiling."""

    def __init__(self):
        # Resolve the root workspace directory dynamically across environments
        self.root_dir = os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(self.root_dir, "goings_os_vault.db")
        self.humanitarian_db = os.path.join(self.root_dir, "choice_legacy_vault.db")
        self.log_path = os.path.join(self.root_dir, "system_faults.log")
        
        # Initialize structured platform logging
        logging.basicConfig(
            filename=self.log_path,
            level=logging.ERROR,
            format="%(asctime)s UTC // SYSTEM_FAULT_TRIGGER // %(message)s"
        )
        self._initialize_core_vault()

    def _initialize_core_vault(self):
        """Initializes database files, forces connection timeouts, and activates WAL mode."""
        try:
            # Injecting a 30 second connection timeout matrix to eliminate concurrency blocks
            connection = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = connection.cursor()
            
            # Activating Write-Ahead Logging mode to allow simultaneous reads and writes
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS b2b_scout_vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    company_name TEXT UNIQUE,
                    contact_email TEXT UNIQUE,
                    contact_phone TEXT,
                    identified_gap TEXT,
                    client_ein TEXT,
                    pipeline_status TEXT
                )
            """)
            connection.commit()
            connection.close()
        except sqlite3.Error as db_init_fault:
            logging.error(f"Database core infrastructure initialization failed: {str(db_init_fault)}")
            raise RuntimeError("Pipeline execution halted; vault initialization failure.")

    def ingest_live_stream_payload(self, inbound_payload: list) -> int:
        """Seals harvested data packages directly into data rows; eliminating production ceilings."""
        inserted_count = 0
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        
        for lead in inbound_payload:
            target_db = self.db_path
            if lead.get("company") and "Choice" in lead["company"]:
                target_db = self.humanitarian_db
            try:
                connection = sqlite3.connect(target_db, timeout=30.0)
                cursor = connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS b2b_scout_vault (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        company_name TEXT UNIQUE,
                        contact_email TEXT UNIQUE,
                        contact_phone TEXT,
                        identified_gap TEXT,
                        client_ein TEXT,
                        pipeline_status TEXT
                    )
                """)
                cursor.execute("""
                    INSERT OR IGNORE INTO b2b_scout_vault (
                        timestamp, company_name, contact_email, contact_phone, identified_gap, client_ein, pipeline_status
                     ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (timestamp, lead["company"], lead["email"], lead["phone"], lead["market_gap"], lead["ein"], "UNTOUCHED_PROSPECT"))
                if cursor.rowcount > 0:
                    inserted_count += 1
                connection.commit()
                connection.close()
            except sqlite3.Error as write_fault:
                logging.error(f"Data write failure encountered during target ingestion: {str(write_fault)}")
                
        return inserted_count


if __name__ == "__main__":
    scout = GarnetScoutEngine()
    print("📡 [GARNET SCOUT] Initializing unchained enterprise ingestion sequence...")
    
    # Ready to receive data from any webhook, API configuration, or stream asset
    live_stream_mock = [
        {
            "company": "Fluke Defense Logistics Ltd",
            "email": "procurement@flukedefense.com",
            "phone": "757-555-0144",
            "market_gap": "Lacking automated compliance data insulation layers",
            "ein": "93-9991234"
        },
        {
            "company": "Atlantic Maritime Fleet Corp",
            "email": "operations@atlanticmaritime.com",
            "phone": "757-555-0199",
            "market_gap": "Manifest tracking software vulnerable to data collisions",
            "ein": "93-8885678"
        }
    ]
    
    records_saved = scout.ingest_live_stream_payload(live_stream_mock)
    print(f"✅ SUCCESS: {records_saved} new unique targets committed to WAL repository lines.")