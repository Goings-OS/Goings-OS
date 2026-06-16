import os
import sys
import sqlite3
import json
import time
from abc import ABC, abstractmethod

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class LocalSQLiteCacheHandler:
    """Manages immediate session logs and transaction state states locally in SQLite database files."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_cache_table()

    def _initialize_cache_table(self):
        """Prepares database cache table and engages WAL journal mode natively."""
        try:
            connection = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_memory_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    context_key TEXT,
                    context_value TEXT,
                    metadata_json TEXT
                )
            """)
            connection.commit()
            connection.close()
        except sqlite3.Error as err:
            sys.stderr.write(f"Cache initialization failure: {str(err)}\n")

    def insert_cache_record(self, key: str, value: str, metadata: dict):
        """Appends a new state context record into the local cache structure."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        metadata_str = json.dumps(metadata)
        try:
            connection = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO session_memory_cache (timestamp, context_key, context_value, metadata_json)
                VALUES (?, ?, ?, ?)
            """, (timestamp, key, value, metadata_str))
            connection.commit()
            connection.close()
        except sqlite3.Error as err:
            sys.stderr.write(f"Cache insert failure: {str(err)}\n")

    def query_cache_records(self, query_metadata: dict) -> list[dict]:
        """Queries and returns local cache records matching specified metadata criteria."""
        results = []
        try:
            connection = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("SELECT timestamp, context_key, context_value, metadata_json FROM session_memory_cache")
            rows = cursor.fetchall()
            connection.close()

            for row in rows:
                timestamp, key, value, meta_str = row
                try:
                    meta_dict = json.loads(meta_str)
                except json.JSONDecodeError:
                    meta_dict = {}

                # Check if all query metadata key: value pairs exist in the stored metadata
                match = True
                for qk, qv in query_metadata.items():
                    if meta_dict.get(qk) != qv:
                        match = False
                        break

                if match:
                    results.append({
                        "timestamp": timestamp,
                        "context_key": key,
                        "context_value": value,
                        "metadata": meta_dict
                    })
        except sqlite3.Error as err:
            sys.stderr.write(f"Cache query failure: {str(err)}\n")
        
        return results


class FirebaseSemanticConnector(ABC):
    """Abstract connector class prepared to sync long-term semantic embeddings with Firebase."""

    @abstractmethod
    def sync_semantic_embedding(self, key: str, embedding_vector: list[float], metadata: dict) -> bool:
        """Abstract hook: synchronizes high-dimensional context vectors with firestore memory vaults."""
        pass

    @abstractmethod
    def retrieve_semantic_context(self, embedding_vector: list[float], threshold: float = 0.8) -> list[dict]:
        """Abstract hook: performs remote vector similarity search inside the cloud environment."""
        pass


class MockFirebaseConnector(FirebaseSemanticConnector):
    """Mock implementation of the Firebase connector for local validation passes."""

    def sync_semantic_embedding(self, key: str, embedding_vector: list[float], metadata: dict) -> bool:
        # Simulate successful synchronization to Firebase Cloud
        return True

    def retrieve_semantic_context(self, embedding_vector: list[float], threshold: float = 0.8) -> list[dict]:
        # Return a mock semantic context record
        return [{"key": "mock_firebase_key", "similarity": 0.95, "context": "Cloud aligned semantic memory node"}]


class PersistentMemoryBank:
    """Coordinates the dual-layer memory graph: integrating local caching and long-term syncing."""

    def __init__(self, db_path: str = None, firebase_connector: FirebaseSemanticConnector = None):
        self.root_dir = os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = db_path or os.path.join(self.root_dir, "goings_os_vault.db")
        self.humanitarian_db = os.path.join(self.root_dir, "choice_legacy_vault.db")

        # Initialize dedicated cache handlers for for-profit and non-profit tenants
        self.commercial_handler = LocalSQLiteCacheHandler(self.db_path)
        self.humanitarian_handler = LocalSQLiteCacheHandler(self.humanitarian_db)

        # Utilize mock connector if none is provided
        self.firebase_connector = firebase_connector or MockFirebaseConnector()

    def store_context(self, context_key: str, context_value: str, metadata: dict, tenant: str = "Goings OS"):
        """Stores situational context key: value parameters into the appropriate database vault."""
        # Segregate CHOICE Inc philanthropic data from commercial data
        if tenant == "Choice Inc" or "choice" in context_key.lower() or "choice" in str(metadata).lower():
            handler = self.humanitarian_handler
            active_tenant = "Choice Inc"
        else:
            handler = self.commercial_handler
            active_tenant = "Goings OS"

        # 1. Log to local SQLite relational cache
        handler.insert_cache_record(context_key, context_value, metadata)
        print(f" -> Memory Bank: Local cache write complete for tenant: {active_tenant}")

        # 2. Sync to Firebase Cloud if semantic embeddings are provided
        if "vector_embeddings" in metadata:
            vector = metadata["vector_embeddings"]
            sync_ok = self.firebase_connector.sync_semantic_embedding(context_key, vector, metadata)
            if sync_ok:
                print(" -> Memory Bank: Firebase semantic embedding synchronization complete")

    def retrieve_context(self, query_metadata: dict, tenant: str = "Goings OS") -> list[dict]:
        """Queries past session contexts and structural profiles from the appropriate cache."""
        if tenant == "Choice Inc" or "choice" in str(query_metadata).lower():
            handler = self.humanitarian_handler
        else:
            handler = self.commercial_handler

        return handler.query_cache_records(query_metadata)


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS STATEFUL PERSISTENT MEMORY BANK    ")
    print("==========================================================")
    
    memory = PersistentMemoryBank()
    
    # Store a mock commercial transaction profile context
    meta_commercial = {"category": "commercial_contracts", "party": "Lizzen", "vector_embeddings": [0.12, -0.45, 0.78]}
    memory.store_context(
        "NTC_LIZZEN_CONTRACT_2026",
        "Talent Engagement Contract: value 12,000.00 USD: Carnival Sunshine venue",
        meta_commercial,
        tenant="Goings OS"
    )
    
    # Retrieve the stored profile context
    search_query = {"party": "Lizzen"}
    retrieved = memory.retrieve_context(search_query, tenant="Goings OS")
    
    print(f"\nRetrieved Context Records count: {len(retrieved)}")
    if retrieved:
        print(f" -> Key: {retrieved[0]['context_key']}")
        print(f" -> Value: {retrieved[0]['context_value']}")
        print(f" -> Metadata: {retrieved[0]['metadata']}")
    print("==========================================================")
