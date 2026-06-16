# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: CORE SWARM STRESS TESTING & CONCURRENCY QUALITY ASSURANCE
# COMPLIANCE: ZERO EM-DASHES; STANDARD UNITTEST ALIGNMENT
# ==============================================================================

import os
import sqlite3
import sys
import unittest

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class TestGoingsOSSwarm(unittest.TestCase):
    """Verifies internal database environment state configurations before cloud transmission."""

    def setUp(self):
        self.root_dir = os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(self.root_dir, "goings_os_vault.db")

    def test_database_wal_journal_mode(self):
        """Validates that the database files run under Write-Ahead Logging safety rules."""
        for db_name in ["goings_os_vault.db", "choice_legacy_vault.db"]:
            db_path = os.path.join(self.root_dir, db_name)
            if os.path.exists(db_path):
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                cursor.execute("PRAGMA journal_mode;")
                mode = cursor.fetchone()[0]
                connection.close()
                self.assertEqual(mode.lower(), "wal", f"{db_name} must operate in WAL mode for multi-agent loops.")
            else:
                self.assertTrue(True)


class TestSwarmManager(unittest.TestCase):
    """Verifies Orchestrator cognitive loops, database logging, and compliance guardrails."""

    def setUp(self):
        from swarm_manager import Orchestrator
        self.orchestrator = Orchestrator()

    def test_critic_compliance_checks(self):
        """Verifies that the Critic successfully identifies compliance guideline violations."""
        # Test em-dash rejection
        ok, msg = self.orchestrator.execute_critic_compliance_check("Compliance payload — invalid.")
        self.assertFalse(ok)
        self.assertIn("strictly prohibited", msg)

        # Test terminology rejection
        ok, msg = self.orchestrator.execute_critic_compliance_check("Deploying to the global governor server.")
        self.assertFalse(ok)
        self.assertIn("Terminology mandate violation", msg)

        # Test standard compliant output
        ok, msg = self.orchestrator.execute_critic_compliance_check("Secured using the Private Governor.")
        self.assertTrue(ok)

    def test_refinement_loop_success(self):
        """Ensures the Worker-Critic loop runs and refines output until compliant."""
        node = self.orchestrator.add_task("TEST-TASK-ID-999", "Sync Choice non-profit logs")
        result = self.orchestrator.process_task_execution_loop(node)
        
        self.assertEqual(result, "SUCCESS")
        self.assertEqual(node.status, "COMPLETED")
        self.assertGreaterEqual(node.refinement_count, 1)
        self.assertNotIn("—", node.output)
        self.assertNotIn("public governor", node.output)
        self.assertIn("Private Governor", node.output)

    def test_tenant_database_isolation(self):
        """Validates that choice-related intents route logs to choice_legacy_vault.db only."""
        # Clean test records first
        for db in [self.orchestrator.db_path, self.orchestrator.humanitarian_db]:
            if os.path.exists(db):
                conn = sqlite3.connect(db)
                conn.execute("DELETE FROM swarm_task_logs WHERE task_id='TEST-ISOLATION-ID'")
                conn.commit()
                conn.close()

        # 1. Non-profit Choice task should go to choice_legacy_vault.db
        node_choice = self.orchestrator.add_task("TEST-ISOLATION-ID", "Process choice grant ledger")
        self.orchestrator.process_task_execution_loop(node_choice)

        # Verify it exists in humanitarian_db
        conn_hum = sqlite3.connect(self.orchestrator.humanitarian_db)
        cur_hum = conn_hum.cursor()
        cur_hum.execute("SELECT status FROM swarm_task_logs WHERE task_id='TEST-ISOLATION-ID'")
        row_hum = cur_hum.fetchone()
        conn_hum.close()
        self.assertIsNotNone(row_hum)

        # Verify it does NOT exist in commercial db_path
        conn_comm = sqlite3.connect(self.orchestrator.db_path)
        cur_comm = conn_comm.cursor()
        cur_comm.execute("SELECT status FROM swarm_task_logs WHERE task_id='TEST-ISOLATION-ID'")
        row_comm = cur_comm.fetchone()
        conn_comm.close()
        self.assertIsNone(row_comm)


if __name__ == "__main__":
    unittest.main()