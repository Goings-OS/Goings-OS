# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: OASIS EXCHANGE FORUM MANAGER (oasis_forum_manager.py)
# COMPLIANCE: ZERO EM-DASHES; PRIVATE GOVERNOR FORMULATIONS
# ==============================================================================

import os
import sys
import time
import json
import sqlite3
from typing import List, Dict, Any

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore
    except AttributeError:
        pass

# Resolve directory paths
FORUM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(FORUM_DIR, "oasis_forum.db")
LOG_PATH = os.path.join(FORUM_DIR, "oasis_forum.log")

class OasisForumManager:
    """Manages the local relational database ledger for background agent collaboration."""

    def __init__(self):
        self._initialize_forum_database()

    def _initialize_forum_database(self):
        """Creates the relational schema tables under local WAL concurrency mode."""
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            
            # 1. Agent Registry Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_registry (
                    agent_name TEXT PRIMARY KEY,
                    gem_role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    version TEXT NOT NULL
                );
            """)

            # 2. Forum Posts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forum_posts (
                    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    post_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    upvotes INTEGER DEFAULT 0,
                    token_efficiency_score REAL NOT NULL,
                    FOREIGN KEY(agent_name) REFERENCES agent_registry(agent_name)
                );
            """)

            # 3. Code Patches Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS code_patches (
                    patch_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    script_name TEXT NOT NULL,
                    patch_content TEXT NOT NULL,
                    FOREIGN KEY(post_id) REFERENCES forum_posts(post_id)
                );
            """)

            conn.commit()
            conn.close()
        except sqlite3.Error as err:
            print(f"[ERROR] Oasis Forum database initialization failed: {str(err)}")
            sys.exit(1)

    def register_agent(self, name: str, role: str, status: str, version: str):
        """Registers a background gem/agent to the active forum board."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO agent_registry (agent_name, gem_role, status, version)
                VALUES (?, ?, ?, ?);
            """, (name, role, status, version))
            conn.commit()
            conn.close()
        except sqlite3.Error as err:
            print(f"[ERROR] Failed to register agent {name}: {str(err)}")

    def create_post(self, agent_name: str, post_type: str, content: str, efficiency: float) -> int:
        """Publishes a new log or update on the decentralized forum board."""
        post_id = -1
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            cursor.execute("""
                INSERT INTO forum_posts (timestamp, agent_name, post_type, content, upvotes, token_efficiency_score)
                VALUES (?, ?, ?, ?, 0, ?);
            """, (timestamp, agent_name, post_type, content, efficiency))
            post_id = cursor.lastrowid if cursor.lastrowid is not None else -1
            conn.commit()
            conn.close()
        except sqlite3.Error as err:
            print(f"[ERROR] Agent {agent_name} failed to publish post: {str(err)}")
        return post_id

    def submit_patch(self, post_id: int, script_name: str, patch_content: str):
        """Attaches a code patch or optimization block to an existing post."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO code_patches (post_id, script_name, patch_content)
                VALUES (?, ?, ?);
            """, (post_id, script_name, patch_content))
            conn.commit()
            conn.close()
        except sqlite3.Error as err:
            print(f"[ERROR] Failed to attach patch to post {post_id}: {str(err)}")

    def upvote_post(self, post_id: int, votes: int = 1):
        """Registers agent consensus upvotes for token-efficient configurations."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE forum_posts SET upvotes = upvotes + ? WHERE post_id = ?;
            """, (votes, post_id))
            conn.commit()
            conn.close()
        except sqlite3.Error as err:
            print(f"[ERROR] Voting execution failed: {str(err)}")

    def get_highest_rated_posts(self) -> List[Dict[str, Any]]:
        """Retrieves outstanding posts categorized by peer review consensus."""
        records = []
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.post_id, p.timestamp, p.agent_name, p.post_type, p.content, p.upvotes, p.token_efficiency_score, c.script_name
                FROM forum_posts p
                LEFT JOIN code_patches c ON p.post_id = c.post_id
                ORDER BY p.upvotes DESC, p.token_efficiency_score DESC;
            """)
            for row in cursor.fetchall():
                records.append(dict(row))
            conn.close()
        except sqlite3.Error as err:
            print(f"[ERROR] Failed to query forum posts: {str(err)}")
        return records


def run_automated_peer_review_loop():
    """Runs a simulated local peer review transaction loop for background agents."""
    print("==============================================================")
    print(" GOINGS OS: INITIALIZING OASIS EXCHANGE FORUM SANDBOX         ")
    print("==============================================================")
    
    manager = OasisForumManager()

    # 1. Register workforce gems
    gems = [
        ("Gem_06_Scout", "Scout", "ONLINE", "v2.1"),
        ("Gem_04_Courier", "Courier", "ONLINE", "v1.8"),
        ("Gem_09_CMO_Catalyst", "Catalyst", "ONLINE", "v3.0"),
        ("Gem_03_Sentry", "Sentry", "ONLINE", "v1.5")
    ]
    for name, role, status, ver in gems:
        manager.register_agent(name, role, status, ver)
    
    print("[FORUM] All background gems registered to local database ledger.")

    # 2. Scout publishes a nightlife sweep log post
    p1 = manager.create_post(
        agent_name="Gem_06_Scout",
        post_type="LOG_TRANSACTION",
        content="Completed 03:00 AM data sweep across regional 757 nightlife footprints: indexed 12 un-insulated venue nodes.",
        efficiency=98.5
    )
    
    # 3. Courier publishes a script patch post
    p2 = manager.create_post(
        agent_name="Gem_04_Courier",
        post_type="CODE_OPTIMIZATION",
        content="Released optimization patch to speed up SQLite WAL check timeouts in off-grid mode.",
        efficiency=99.2
    )
    manager.submit_patch(
        post_id=p2,
        script_name="off_grid_protocol.py",
        patch_content="def verify_wal():\n    # Strict local isolation checking\n    conn = sqlite3.connect('goings_os_vault.db', timeout=5.0)\n    ..."
    )

    # 4. Sentry and Catalyst upvote the token-efficient code configuration
    manager.upvote_post(post_id=p2, votes=3)
    manager.upvote_post(post_id=p1, votes=1)
    
    print("[FORUM] Asynchronous peer review loop executed successfully.")
    print("[FORUM] Fetching live reviews board telemetry...")
    print("--------------------------------------------------------------")

    # Output logs to screen
    posts = manager.get_highest_rated_posts()
    for post in posts:
        print(f"[{post['timestamp']}] [Post {post['post_id']}] Agent: {post['agent_name']}")
        print(f" -> Type: {post['post_type']}")
        print(f" -> Details: {post['content']}")
        if post['script_name']:
            print(f" -> Target Script: {post['script_name']}")
        print(f" -> Peer Upvotes: {post['upvotes']} | Efficiency: {post['token_efficiency_score']}%")
        print("--------------------------------------------------------------")


if __name__ == "__main__":
    run_automated_peer_review_loop()
