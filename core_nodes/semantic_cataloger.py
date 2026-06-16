# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: WORKSPACE SEMANTIC CATALOGER & VECTOR SEARCH GRAPH
# COMPLIANCE: ZERO EM-DASHES; INCREMENTAL FILE INDEXING
# ==============================================================================

import os
import sys
import re
import time
import json
import sqlite3
import hashlib

# Ensure parent directory is in sys.path when running this module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class SemanticCataloger:
    """Recursively indexes workspace resources and supports vector similarity queries locally."""

    def __init__(self, db_path: str = None):
        self.root_dir = os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = db_path or os.path.join(self.root_dir, "catalog_manifest.db")
        self._initialize_database()

    def _initialize_database(self):
        """Creates the manifest database schema and enables Write-Ahead Logging concurrency."""
        try:
            connection = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workspace_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    content_hash TEXT,
                    content TEXT,
                    embedding_json TEXT,
                    last_indexed TEXT
                )
            """)
            connection.commit()
            connection.close()
        except sqlite3.Error as err:
            sys.stderr.write(f"Catalog database initialization failure: {str(err)}\n")

    def generate_embeddings(self, text: str) -> list[float]:
        """Converts text content into a normalized semantic vector using a deterministic hashing vectorizer."""
        dimensions = 128
        vector = [0.0] * dimensions

        # Tokenize text into words/alphanumeric sequences
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vector

        # Perform deterministic hash routing for each word
        for word in words:
            h = 0
            for char in word:
                h = (h * 31 + ord(char)) % dimensions
            vector[h] += 1.0

        # Normalize the dense vector to unit length (L2 norm)
        magnitude = sum(x * x for x in vector) ** 0.5
        if magnitude > 0.0:
            vector = [x / magnitude for x in vector]

        return vector

    def index_workspace(self, target_directory: str):
        """Recursively scans the target directory and indexes text files incrementally."""
        if not os.path.exists(target_directory):
            print(f" -> Cataloger Warn: Target path '{target_directory}' does not exist: skipping crawler run")
            return

        # Directories to exclude from indexing
        exclude_dirs = {".git", "__pycache__", ".vscode", "node_modules", ".gemini", "vite-monorepo", "next-app"}
        # File extensions to include in index
        include_extensions = {".py", ".txt", ".md", ".json", ".csv", ".html", ".js", ".ts"}

        indexed_count = 0
        skipped_count = 0

        for root, dirs, files in os.walk(target_directory):
            # Modify dirs in-place to skip excluded directories during traversal
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in include_extensions:
                    continue

                file_path = os.path.join(root, file)
                
                try:
                    # 1. Compute content MD5 hash for incremental check
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    md5_hash = hashlib.md5(file_data).hexdigest()

                    # 2. Check if file is already indexed with the same hash
                    if self._is_file_unchanged(file_path, md5_hash):
                        skipped_count += 1
                        continue

                    # 3. Read content (safely decoding binary/mixed encodings)
                    content_str = file_data.decode("utf-8", errors="ignore")

                    # 4. Generate semantic vectors
                    vector = self.generate_embeddings(content_str)
                    vector_json = json.dumps(vector)

                    # 5. Upsert indexing metrics in manifest database
                    self._upsert_index_record(file_path, md5_hash, content_str, vector_json)
                    indexed_count += 1

                except (IOError, OSError) as err:
                    sys.stderr.write(f"Cataloger File error for '{file_path}': {str(err)}\n")

        print(f" -> Workspace Index Complete: {indexed_count} indexed: {skipped_count} skipped (unchanged)")

    def _is_file_unchanged(self, file_path: str, current_hash: str) -> bool:
        """Queries manifest to verify if the file has already been indexed with the matching hash."""
        unchanged = False
        try:
            connection = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("SELECT content_hash FROM workspace_index WHERE file_path = ?", (file_path,))
            row = cursor.fetchone()
            connection.close()
            if row and row[0] == current_hash:
                unchanged = True
        except sqlite3.Error:
            pass
        return unchanged

    def _upsert_index_record(self, file_path: str, file_hash: str, content: str, embedding_json: str):
        """Inserts or replaces a file's indexing data in the SQLite catalog."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        try:
            connection = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO workspace_index (file_path, content_hash, content, embedding_json, last_indexed)
                VALUES (?, ?, ?, ?, ?)
            """, (file_path, file_hash, content, embedding_json, timestamp))
            connection.commit()
            connection.close()
        except sqlite3.Error as err:
            sys.stderr.write(f"Cataloger database upsert failure: {str(err)}\n")

    def query_graph(self, query_text: str, top_k: int = 5, threshold: float = 0.0) -> list[dict]:
        """Calculates cosine similarity metrics for all indexed documents against the query vector."""
        query_vector = self.generate_embeddings(query_text)
        results = []

        try:
            connection = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("SELECT file_path, content, embedding_json FROM workspace_index")
            rows = cursor.fetchall()
            connection.close()

            for row in rows:
                file_path, content, emb_json = row
                try:
                    doc_vector = json.loads(emb_json)
                except json.JSONDecodeError:
                    continue

                # Cosine similarity is exactly the dot product since both vectors are normalized
                similarity = sum(qv * dv for qv, dv in zip(query_vector, doc_vector))

                if similarity >= threshold:
                    # Provide text excerpt preview
                    preview = content[:200] + "..." if len(content) > 200 else content
                    results.append({
                        "file_path": file_path,
                        "similarity": similarity,
                        "content_preview": preview
                    })

            # Sort results descending by score
            results.sort(key=lambda x: x["similarity"], reverse=True)

        except sqlite3.Error as err:
            sys.stderr.write(f"Cataloger database query failure: {str(err)}\n")

        return results[:top_k]


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS SEMANTIC CATALOGER NODE            ")
    print("==========================================================")
    
    cataloger = SemanticCataloger()
    
    # Index immediate core_nodes directory
    search_dir = os.path.dirname(os.path.abspath(__file__))
    cataloger.index_workspace(search_dir)
    
    # Query graph
    query = "low-latency audio capture stream socket LiveKit"
    matches = cataloger.query_graph(query, top_k=2)
    
    print(f"\nQuery: '{query}'")
    print(f"Found {len(matches)} matches:")
    for idx, match in enumerate(matches, 1):
        print(f" [{idx}] Path: {match['file_path']}")
        print(f"     Similarity score: {match['similarity']:.4f}")
    print("==========================================================")
