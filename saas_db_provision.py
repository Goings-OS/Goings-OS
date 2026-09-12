# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: MULTI-TENANT SAAS DATABASE PROVISIONER (saas_db_provision.py)
# COMPLIANCE: ZERO EM-DASHES; PRIVATE GOVERNOR FORMULATIONS
# ==============================================================================

import os
import sys
import sqlite3
import time
from typing import List, Dict, Any

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore
    except AttributeError:
        pass

DB_PATH = "saas_platform_multi_tenant.db"


class MultiTenantDatabaseManager:
    """Manages multi-tenant relational schemas and enforces logical tenant isolation."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Creates the multi-tenant relational schema with foreign key enforcement."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enforce foreign key constraints natively in SQLite
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("PRAGMA journal_mode=WAL;")

            # 1. Tenants Master Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tenants (
                    tenant_id TEXT PRIMARY KEY,
                    organization_name TEXT NOT NULL,
                    subscription_tier TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)

            # 2. Tenant Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tenant_users (
                    user_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id) ON DELETE CASCADE
                );
            """)

            # 3. Tenant Data Table (Data Ingress Repository)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tenant_data (
                    data_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    data_key TEXT NOT NULL,
                    data_value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id) ON DELETE CASCADE
                );
            """)

            conn.commit()
            conn.close()
        except sqlite3.Error as init_fault:
            print(f"[DATABASE] [CRITICAL] Failed to provision schemas: {str(init_fault)}")
            sys.exit(1)


class TenantSession:
    """Simulates PostgreSQL Row-Level Security (RLS) by enforcing tenant_id parameters."""

    def __init__(self, manager: MultiTenantDatabaseManager, tenant_id: str):
        self.manager = manager
        self.tenant_id = tenant_id
        self._verify_tenant_exists()

    def _verify_tenant_exists(self):
        """Verifies that the tenant is registered in the master table before opening session."""
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM tenants WHERE tenant_id = ?;", (self.tenant_id,))
        exists = cursor.fetchone()
        conn.close()
        if not exists:
            raise ValueError(f"Access Denied: Tenant ID '{self.tenant_id}' is not registered.")

    def insert_tenant_user(self, user_id: str, username: str, email: str):
        """Secured Insert: Inserts a user bound to this session's tenant_id."""
        try:
            conn = sqlite3.connect(self.manager.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            
            cursor.execute("""
                INSERT INTO tenant_users (user_id, tenant_id, username, email, created_at)
                VALUES (?, ?, ?, ?, ?);
            """, (user_id, self.tenant_id, username, email, timestamp))
            
            conn.commit()
            conn.close()
            print(f"[RLS_SESSION] [{self.tenant_id}] Inserted User '{username}' successfully.")
        except sqlite3.Error as query_fault:
            print(f"[RLS_SESSION] [{self.tenant_id}] [ERROR] User insert failed: {str(query_fault)}")

    def insert_tenant_data(self, data_id: str, data_key: str, data_value: str):
        """Secured Insert: Inserts data records bound to this session's tenant_id."""
        try:
            conn = sqlite3.connect(self.manager.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            
            cursor.execute("""
                INSERT INTO tenant_data (data_id, tenant_id, data_key, data_value, created_at)
                VALUES (?, ?, ?, ?, ?);
            """, (data_id, self.tenant_id, data_key, data_value, timestamp))
            
            conn.commit()
            conn.close()
            print(f"[RLS_SESSION] [{self.tenant_id}] Inserted key '{data_key}' successfully.")
        except sqlite3.Error as query_fault:
            print(f"[RLS_SESSION] [{self.tenant_id}] [ERROR] Data insert failed: {str(query_fault)}")

    def get_tenant_data(self) -> List[Dict[str, Any]]:
        """Secured Query: Retrieves only the records belonging to this session's tenant_id."""
        records = []
        try:
            conn = sqlite3.connect(self.manager.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Enforce strict isolation: filtering only by the session tenant_id
            cursor.execute("""
                SELECT data_id, data_key, data_value, created_at 
                FROM tenant_data 
                WHERE tenant_id = ?;
            """, (self.tenant_id,))
            
            for row in cursor.fetchall():
                records.append(dict(row))
            conn.close()
        except sqlite3.Error as query_fault:
            print(f"[RLS_SESSION] [{self.tenant_id}] [ERROR] Query failed: {str(query_fault)}")
        return records


def run_provisioning_test():
    print("==============================================================")
    print(" GOINGS OS: PROVISIONING MULTI-TENANT SAAS DATABASE PLATFORM  ")
    print("==============================================================")
    
    manager = MultiTenantDatabaseManager()
    
    # Register core tenants
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    
    tenants = [
        ("TENANT-KIG-CONSULTING", "Keep It Goings Consulting", "Enterprise"),
        ("TENANT-LAEC-HAMPTON", "Luxury Affairs Event Center", "Premium")
    ]
    
    for t_id, t_name, t_tier in tenants:
        cursor.execute("""
            INSERT OR REPLACE INTO tenants (tenant_id, organization_name, subscription_tier, created_at)
            VALUES (?, ?, ?, ?);
        """, (t_id, t_name, t_tier, timestamp))
        
    conn.commit()
    conn.close()
    print("[DATABASE] Tenants registered successfully.")

    # Open isolated sessions
    session_kig = TenantSession(manager, "TENANT-KIG-CONSULTING")
    session_laec = TenantSession(manager, "TENANT-LAEC-HAMPTON")

    # Add isolated records
    session_kig.insert_tenant_user("usr_001", "terrence_goings", "info@goingsos.com")
    session_kig.insert_tenant_data("dat_001", "weekly_revenue_floor", "5000.00")
    
    session_laec.insert_tenant_user("usr_002", "laec_manager", "venue@luxuryaffairs.com")
    session_laec.insert_tenant_data("dat_002", "ntc_base_deposit", "150.00")

    # Query KIG Consulting data
    print("\n--- QUERYING KIG CONSULTING DATA SESSION ---")
    kig_records = session_kig.get_tenant_data()
    for rec in kig_records:
        print(f" -> ID: {rec['data_id']} | Key: {rec['data_key']} | Value: {rec['data_value']}")

    # Query Luxury Affairs data
    print("\n--- QUERYING LUXURY AFFAIRS DATA SESSION ---")
    laec_records = session_laec.get_tenant_data()
    for rec in laec_records:
        print(f" -> ID: {rec['data_id']} | Key: {rec['data_key']} | Value: {rec['data_value']}")

    print("==============================================================")


if __name__ == "__main__":
    run_provisioning_test()
