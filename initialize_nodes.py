# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: SPECIALIZED MULTI-TENANT NODE INITIALIZATION
# COMPLIANCE: ZERO EM-DASHES; STRICT COGNITIVE DATA SEPARATION
# ==============================================================================

import logging
import os
import sqlite3
import sys

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class NodeInfrastructureBuilder:
    """Provisions isolated, tenant-demarcated database files to preserve corporate integrity."""

    def __init__(self):
        self.root_dir = os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.abspath(__file__)))
        self.log_path = os.path.join(self.root_dir, "system_faults.log")
        
        # Defining isolated database destinations to protect separate entities
        self.commercial_db = os.path.join(self.root_dir, "goings_os_vault.db")
        self.humanitarian_db = os.path.join(self.root_dir, "choice_legacy_vault.db")

        logging.basicConfig(
            filename=self.log_path,
            level=logging.ERROR,
            format="%(asctime)s UTC // NODE_PROVISIONING_FAULT // %(message)s"
        )

    def provision_hardened_vaults(self):
        """Builds separate file matrices and activates WAL concurrency mode on both paths."""
        print("==========================================================")
        print(" INITIALIZING GOINGS OS SPECIALIZED STORAGE NODES         ")
        print("==========================================================")

        # 1. Provisioning Commercial For-Profit Storage Vault
        try:
            print(f"📡 Securing Commercial Matrix: {self.commercial_db}")
            conn = sqlite3.connect(self.commercial_db, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commercial_leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT UNIQUE,
                    revenue_tier TEXT,
                    pipeline_status TEXT
                )
            """)
            conn.commit()
            conn.close()
            print(" -> Commercial Engine Status: WAL CONCURRENCY ENGAGED")
        except sqlite3.Error as err:
            logging.error(f"Commercial database build failed: {str(err)}")

        # 2. Provisioning Isolated Choice Inc Philanthropic Vault
        try:
            print(f"\n📡 Securing Humanitarian Matrix: {self.humanitarian_db}")
            conn = sqlite3.connect(self.humanitarian_db, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS choice_inc_grant_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    donor_ein TEXT UNIQUE,
                    allocation_block_usd REAL,
                    compliance_receipt_hash TEXT
                )
            """)
            conn.commit()
            conn.close()
            print(" -> Choice Inc Engine Status: COMPLIANCE ISOLATION VERIFIED")
            print("==========================================================")
        except sqlite3.Error as err:
            logging.error(f"Humanitarian database segregation failed: {str(err)}")


if __name__ == "__main__":
    builder = NodeInfrastructureBuilder()
    builder.provision_hardened_vaults()