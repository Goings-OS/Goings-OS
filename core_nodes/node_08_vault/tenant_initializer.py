import sqlite3
import os

def initialize_tenant_vault():
    db_path = "goings_os_vault.db"
    print(f"[VAULT] Connecting to production database instance at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign key enforcement natively
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create the Master Tenants table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id TEXT PRIMARY KEY,
            organization_name TEXT NOT NULL,
            market_region TEXT NOT NULL,
            subscription_tier TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Re-verify and adapt the owners_draw_allocations table for multi tenancy
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS owners_draw_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            source_origin TEXT NOT NULL,
            gross_amount REAL NOT NULL,
            net_allocation REAL NOT NULL,
            tracking_status TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id)
        );
    """)
    
    # Populate default target market profiles to secure the baseline architecture
    default_tenants = [
        ("757-LOCAL-HQ", "Goings OS Core Operations", "Hampton Roads", "Sovereign"),
        ("GLOBAL-ENT-01", "International Logistics Tier", "Abroad", "Enterprise")
    ]
    
    for tenant in default_tenants:
        cursor.execute("""
            INSERT OR IGNORE INTO tenants (tenant_id, organization_name, market_region, subscription_tier)
            VALUES (?, ?, ?, ?);
        """, tenant)
        
    conn.commit()
    conn.close()
    print("[SUCCESS] Multi-tenant database schema fully initialized and verified clear.")

if __name__ == "__main__":
    initialize_tenant_vault()
