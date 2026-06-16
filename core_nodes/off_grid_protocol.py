# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: PRIVATE OFF-GRID PLATFORM & FAILOVER SYSTEM
# COMPLIANCE: ZERO EM-DASHES; SATELLITE BATCH-SYNC & SQL OFFLINE QUEUEING
# ==============================================================================

import os
import sys
import time
import json
import sqlite3

# Ensure parent directory is in sys.path when running this module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class SatelliteBackhaul:
    """Manages high-latency satellite-based batch communication links (e.g. Starlink)."""

    def __init__(self, latency_ms: float = 240.0):
        self.latency_ms = latency_ms

    def batch_sync(self, states: list[dict]) -> bool:
        """Transmits state packages in batches optimized for high-latency sat-comm backhauls."""
        if not states:
            return True

        packet_size = len(json.dumps(states).encode("utf-8"))
        print(f"\n📡 [SAT-COMM] Handshaking with Starlink backhaul satellite array...")
        print(f" -> Transmitting batch of {len(states)} states: Size: {packet_size} bytes")
        
        # Simulate satellite latency delay
        time.sleep(self.latency_ms / 1000.0)
        
        print(f" -> Sat-Comm Sync: Successfully synced batch in {self.latency_ms:.2f} milliseconds")
        return True


class LocalQueueSubstrate:
    """Manages local SQLite database queue tables for offline payload preservation."""

    def __init__(self, root_dir: str = None):
        self.root_dir = root_dir or os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.commercial_db = os.path.join(self.root_dir, "goings_os_vault.db")
        self.humanitarian_db = os.path.join(self.root_dir, "choice_legacy_vault.db")
        self._initialize_queue_tables()

    def _initialize_queue_tables(self):
        """Creates the offline queue table in both database vaults (WAL mode engaged)."""
        for path in [self.commercial_db, self.humanitarian_db]:
            try:
                connection = sqlite3.connect(path, timeout=30.0)
                cursor = connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS off_grid_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        task_id TEXT,
                        payload_json TEXT
                    )
                """)
                connection.commit()
                connection.close()
            except sqlite3.Error as err:
                sys.stderr.write(f"Queue initialization failure for {path}: {str(err)}\n")

    def _get_db_path(self, tenant: str) -> str:
        """Segregates Choice Inc database routing from commercial Goings OS data."""
        if tenant == "Choice Inc":
            return self.humanitarian_db
        return self.commercial_db

    def enqueue_payload(self, task_id: str, payload: dict, tenant: str = "Goings OS") -> bool:
        """Stores an outbound API payload into the localized SQLite queue during blackouts."""
        db_path = self._get_db_path(tenant)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        payload_str = json.dumps(payload)

        try:
            connection = sqlite3.connect(db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO off_grid_queue (timestamp, task_id, payload_json)
                VALUES (?, ?, ?)
            """, (timestamp, task_id, payload_str))
            connection.commit()
            connection.close()
            print(f" -> Local Queue: Enqueued offline task '{task_id}' for tenant: {tenant}")
            return True
        except sqlite3.Error as err:
            sys.stderr.write(f"Local Queue enqueue failure: {str(err)}\n")
            return False

    def dequeue_payloads(self, tenant: str = "Goings OS") -> list[dict]:
        """Retrieves all queued offline payloads stored in the tenant vault."""
        db_path = self._get_db_path(tenant)
        results = []

        try:
            connection = sqlite3.connect(db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("SELECT id, task_id, payload_json FROM off_grid_queue ORDER BY id ASC")
            rows = cursor.fetchall()
            connection.close()

            for row in rows:
                item_id, task_id, payload_str = row
                try:
                    payload = json.loads(payload_str)
                except json.JSONDecodeError:
                    payload = {}
                results.append({
                    "id": item_id,
                    "task_id": task_id,
                    "payload": payload
                })
        except sqlite3.Error as err:
            sys.stderr.write(f"Local Queue dequeue failure: {str(err)}\n")

        return results

    def clear_queue(self, item_ids: list[int], tenant: str = "Goings OS"):
        """Deletes processed payload records from the local SQLite queue."""
        if not item_ids:
            return
        db_path = self._get_db_path(tenant)
        
        try:
            connection = sqlite3.connect(db_path, timeout=30.0)
            cursor = connection.cursor()
            placeholders = ",".join("?" for _ in item_ids)
            cursor.execute(f"DELETE FROM off_grid_queue WHERE id IN ({placeholders})", item_ids)
            connection.commit()
            connection.close()
            print(f" -> Local Queue: Cleared {len(item_ids)} sync records from database for tenant: {tenant}")
        except sqlite3.Error as err:
            sys.stderr.write(f"Local Queue purge failure: {str(err)}\n")


class OffGridController:
    """Monitors heartbeat connectivity, triggers offline queueing, and flushes queues to sat-comm."""

    def __init__(self, root_dir: str = None, sat_comm: SatelliteBackhaul = None):
        self.root_dir = root_dir or os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.local_queue = LocalQueueSubstrate(self.root_dir)
        self.sat_comm = sat_comm or SatelliteBackhaul()
        self.network_connected = True

    def check_heartbeat(self) -> bool:
        """Polls connectivity status to determine if failover switching is required."""
        return self.network_connected

    def send_payload(self, task_id: str, payload: dict, tenant: str = "Goings OS") -> dict:
        """Sends data directly if online, or redirects to local queue during blackouts."""
        if self.check_heartbeat():
            print(f" -> Transmission: Direct online sync successful for Task: {task_id}")
            return {
                "status": "SYNCED_ONLINE",
                "task_id": task_id,
                "payload": payload
            }
        else:
            # Re-routed to Option B: Local Queue Substrate
            self.local_queue.enqueue_payload(task_id, payload, tenant)
            return {
                "status": "QUEUED_OFFLINE",
                "task_id": task_id,
                "payload": payload
            }

    def autonomous_switch(self, connection_state: bool) -> bool:
        """Seamlessly transitions routing structures between online state and local backup queueing."""
        if connection_state == self.network_connected:
            return False

        if connection_state:
            print("\n📶 [OFF-GRID CONTROLLER] Network connection restored: ENGAGING ONLINE ROUTING")
            
            # Flush queued offline tasks back to cloud via Sat-Comm array (segregated by tenant)
            for tenant in ["Goings OS", "Choice Inc"]:
                queued_items = self.local_queue.dequeue_payloads(tenant)
                if queued_items:
                    print(f" -> Reconnection: Flushing {len(queued_items)} queued records for tenant: {tenant}")
                    
                    # Package payloads for batch satellite sync
                    payloads = [item["payload"] for item in queued_items]
                    sync_ok = self.sat_comm.batch_sync(payloads)
                    
                    if sync_ok:
                        item_ids = [item["id"] for item in queued_items]
                        self.local_queue.clear_queue(item_ids, tenant)

            self.network_connected = True
        else:
            print("\n📉 [OFF-GRID CONTROLLER] Network blackout detected: ACTIVATING LOCAL QUEUE SUBSTRATE")
            self.network_connected = False

        return True


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS PRIVATE OFF-GRID PROTOCOL NODE     ")
    print("==========================================================")
    
    controller = OffGridController()
    
    # 1. Execute online send
    payload_com = {"leads_count": 12, "benchmark": "weekly_revenue"}
    controller.send_payload("TASK-ONLINE-01", payload_com, tenant="Goings OS")
    
    # 2. Trigger network blackout and execute offline send
    controller.autonomous_switch(False)
    payload_choice = {"grant_id": "CHOICE-2026-99", "allocation": 7500.00}
    controller.send_payload("TASK-OFFLINE-02", payload_choice, tenant="Choice Inc")
    
    # 3. Restore connection and auto-flush
    controller.autonomous_switch(True)
    print("==========================================================")
