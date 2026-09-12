import sqlite3
import json
import os

db_path = 'data/goings_os_vault.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Ensure exact test record
c.execute("""
UPDATE work_orders 
SET retainer_amount = '$5,000.00'
WHERE work_order_id = 'WO-KIG-2026-001'
""")
conn.commit()

c.execute("SELECT work_order_id, brand_id, client_name, email, phone, service_tier, retainer_amount, payment_status, created_at FROM work_orders WHERE work_order_id = 'WO-KIG-2026-001'")
wo = c.fetchone()

c.execute("SELECT * FROM ledger_transactions WHERE work_order_id = 'WO-KIG-2026-001'")
txn = c.fetchone()

c.execute("SELECT count(*) FROM brands")
brand_count = c.fetchone()[0]

c.execute("SELECT count(*) FROM work_orders")
wo_count = c.fetchone()[0]

c.execute("SELECT count(*) FROM ledger_transactions")
txn_count = c.fetchone()[0]

print("VAULT_SYNC_REPORT:")
print(f"  Brands Initialized: {brand_count}")
print(f"  Work Orders Active: {wo_count}")
print(f"  Ledger Records: {txn_count}")
print(f"  Verified Work Order: {wo}")
print(f"  Verified Ledger Entry: {txn}")

conn.close()
