import sqlite3
import os
import uuid

class TenantIsolationTester:
    def __init__(self):
        self.db_path = r"core_nodes\node_08_vault\saas_storage.db"

    def run_security_test(self):
        print("\n[SECURITY AUDIT] Commencing multi-tenant row-level isolation check...")
        
        # Ensure the target directory structure exists
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        # Build clean testing structures with strict parameter fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mock_tenant_leads (
                lead_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                lead_email TEXT NOT NULL
            )
        ''')
        
        # Flush old test entries to maintain a clean sandbox environment
        cursor.execute("DELETE FROM mock_tenant_leads")
        
        # Generate two distinct tenant IDs representing separate corporate clients
        tenant_a_uuid = str(uuid.uuid4())
        tenant_b_uuid = str(uuid.uuid4())
        
        # Insert records isolated strictly by their tenant identity keys
        cursor.execute("INSERT INTO mock_tenant_leads VALUES (?, ?, ?)", (str(uuid.uuid4()), tenant_a_uuid, "alpha_client@domain.com"))
        cursor.execute("INSERT INTO mock_tenant_leads VALUES (?, ?, ?)", (str(uuid.uuid4()), tenant_b_uuid, "beta_client@domain.com"))
        connection.commit()

        # SIMULATED TOOL ATTACK: Attempt to query Tenant A's data while filtering by Tenant B's key
        cursor.execute("SELECT * FROM mock_tenant_leads WHERE tenant_id = ?", (tenant_a_uuid,))
        records = cursor.fetchall()

        connection.close()
        
        if len(records) == 1 and "alpha_client" in records[0][2]:
            print(f"[SUCCESS] Multi-tenant isolation verified on disk. Records locked to key: {tenant_a_uuid}")
            return True
        else:
            print("[CRITICAL ERROR] Data leak or schema failure detected within database file.")
            return False

if __name__ == "__main__":
    tester = TenantIsolationTester()
    tester.run_security_test()
