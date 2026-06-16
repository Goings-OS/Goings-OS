# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: ENTERPRISE EVENT-DRIVEN WORKFLOW AUTOMATION ENGINE
# COMPLIANCE: ZERO EM-DASHES; HIGH-PERFORMANCE ASYNCHRONOUS WORKFLOWS
# ==============================================================================

import os
import sys
import time
import json
import sqlite3
import concurrent.futures

# Ensure parent directory is in sys.path when running this module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class EventAutomationEngine:
    """Coordinates pub-sub listener routing, asynchronous parallel cascades, and transaction logs."""

    def __init__(self, root_dir: str = None, max_workers: int = 5):
        self.root_dir = root_dir or os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.commercial_db = os.path.join(self.root_dir, "goings_os_vault.db")
        self.humanitarian_db = os.path.join(self.root_dir, "choice_legacy_vault.db")
        
        self.listeners = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._initialize_log_tables()

    def _initialize_log_tables(self):
        """Prepares database transaction audit tables in both database vaults (WAL mode engaged)."""
        for path in [self.commercial_db, self.humanitarian_db]:
            try:
                connection = sqlite3.connect(path, timeout=30.0)
                cursor = connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS event_history_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        event_topic TEXT,
                        event_data_json TEXT,
                        listener_callback TEXT,
                        status TEXT
                    )
                """)
                connection.commit()
                connection.close()
            except sqlite3.Error as err:
                sys.stderr.write(f"Event logs table initialization failure for {path}: {str(err)}\n")

    def _get_db_path(self, tenant: str) -> str:
        """Segregates Choice Inc database files from commercial Goings OS data vaults."""
        if tenant == "Choice Inc":
            return self.humanitarian_db
        return self.commercial_db

    def register_event_listener(self, event_topic: str, listener_callback):
        """Maps specific system triggers (topics) to specific execution routines."""
        if not event_topic or not listener_callback:
            raise ValueError("Event topic and callback callable cannot be empty")
        
        if event_topic not in self.listeners:
            self.listeners[event_topic] = []
            
        self.listeners[event_topic].append(listener_callback)
        print(f" -> Event Engine: Registered listener callback '{listener_callback.__name__}' for topic: {event_topic}")

    def _insert_event_log(self, db_path: str, timestamp: str, topic: str, data_json: str, callback_name: str, status: str) -> int:
        """Inserts a pending audit log entry transactionally in SQLite and returns the row id."""
        log_id = -1
        try:
            connection = sqlite3.connect(db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO event_history_log (timestamp, event_topic, event_data_json, listener_callback, status)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, topic, data_json, callback_name, status))
            log_id = cursor.lastrowid
            connection.commit()
            connection.close()
        except sqlite3.Error as err:
            sys.stderr.write(f"Event log insert failure: {str(err)}\n")
        return log_id

    def _update_event_status(self, db_path: str, log_id: int, status: str):
        """Updates the status of a specific event dispatch entry transactionally."""
        try:
            connection = sqlite3.connect(db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("UPDATE event_history_log SET status = ? WHERE id = ?", (status, log_id))
            connection.commit()
            connection.close()
        except sqlite3.Error as err:
            sys.stderr.write(f"Event log update failure: {str(err)}\n")

    def _execute_callback_wrapper(self, db_path: str, log_id: int, callback, event_data: dict):
        """Safely executes the callback, traps exceptions, and updates the database transaction log."""
        try:
            callback(event_data)
            self._update_event_status(db_path, log_id, "COMPLETED")
        except Exception as err:
            err_msg = str(err)
            sys.stderr.write(f"Event callback execution failure: {err_msg}\n")
            self._update_event_status(db_path, log_id, f"FAILED: {err_msg}")

    def trigger_cascade(self, event_topic: str, event_data: dict, tenant: str = "Goings OS") -> list[concurrent.futures.Future]:
        """Spawns parallel agent tasks asynchronously across the ThreadPoolExecutor."""
        listeners = self.listeners.get(event_topic, [])
        if not listeners:
            print(f" -> Event Engine: No registered listeners for topic '{event_topic}': skipping cascade")
            return []

        futures = []
        db_path = self._get_db_path(tenant)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        payload_str = json.dumps(event_data)

        for callback in listeners:
            callback_name = callback.__name__ if hasattr(callback, "__name__") else str(callback)
            
            # 1. Log transaction-safe pending event
            log_id = self._insert_event_log(db_path, timestamp, event_topic, payload_str, callback_name, "PENDING")
            
            # 2. Spawn callback asynchronously in ThreadPoolExecutor
            future = self.executor.submit(self._execute_callback_wrapper, db_path, log_id, callback, event_data)
            futures.append(future)

        print(f" -> Event Engine: Dispatched cascade for '{event_topic}': {len(listeners)} parallel tasks spawned")
        return futures

    def shutdown(self):
        """Cleans up and releases the thread pool resource pool."""
        self.executor.shutdown(wait=True)
        print(" -> Event Engine: ThreadPoolExecutor shut down cleanly")


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS EVENT-DRIVEN AUTOMATION NODE       ")
    print("==========================================================")
    
    engine = EventAutomationEngine()
    
    # Register mock callbacks
    def callback_lead_commercial(data):
        print(f" [Lead Commercial Callback] Syncing new lead: {data['name']} (EIN: {data['ein']})")
        time.sleep(0.1) # Simulate task duration
        
    def callback_notify_sentry(data):
        print(f" [Notify Sentry Callback] Performing security validation for: {data['name']}")
        
    engine.register_event_listener("lead_ingest", callback_lead_commercial)
    engine.register_event_listener("lead_ingest", callback_notify_sentry)
    
    # Trigger cascade
    event_payload = {"name": "Keep It Goings Consulting", "ein": "93-4911193"}
    futures = engine.trigger_cascade("lead_ingest", event_payload, tenant="Goings OS")
    
    # Wait for execution to resolve
    concurrent.futures.wait(futures)
    
    engine.shutdown()
    print("==========================================================")
