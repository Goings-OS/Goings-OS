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


class TestMemoryBank(unittest.TestCase):
    """Verifies dual-layer stateful memory operations: caching: and database routing rules."""

    def setUp(self):
        from core_nodes.memory_bank import PersistentMemoryBank
        self.memory = PersistentMemoryBank()
        # Clean up database cache records before each test runs
        for db in [self.memory.db_path, self.memory.humanitarian_db]:
            if os.path.exists(db):
                conn = sqlite3.connect(db)
                conn.execute("DELETE FROM session_memory_cache")
                conn.commit()
                conn.close()

    def test_store_and_retrieve_context(self):
        """Validates storing and retrieving context records from the relational cache."""
        meta = {"category": "test_memories", "session_id": "999-alpha"}
        self.memory.store_context("TEST-KEY-1", "Test value data segment", meta, tenant="Goings OS")

        retrieved = self.memory.retrieve_context({"session_id": "999-alpha"}, tenant="Goings OS")
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0]["context_key"], "TEST-KEY-1")
        self.assertEqual(retrieved[0]["context_value"], "Test value data segment")
        self.assertEqual(retrieved[0]["metadata"]["category"], "test_memories")

    def test_memory_tenant_isolation(self):
        """Verifies that Choice-related memory records are routed to choice_legacy_vault.db only."""
        meta = {"category": "humanitarian_grants", "allocation": 10000.00}
        
        # Store context with Choice Inc tenant context
        self.memory.store_context("CHOICE-GRANT-TEST-KEY", "Grant disbursement details", meta, tenant="Choice Inc")

        # Query from Choice Inc database
        retrieved_hum = self.memory.retrieve_context({"category": "humanitarian_grants"}, tenant="Choice Inc")
        self.assertEqual(len(retrieved_hum), 1)
        self.assertEqual(retrieved_hum[0]["context_key"], "CHOICE-GRANT-TEST-KEY")

        # Query from Goings OS database: should be empty
        retrieved_comm = self.memory.retrieve_context({"category": "humanitarian_grants"}, tenant="Goings OS")
        self.assertEqual(len(retrieved_comm), 0)


class TestAgentSecurity(unittest.TestCase):
    """Verifies cryptographic token signature generation and verification rules."""

    def setUp(self):
        from core_nodes.agent_security import GemIdentityManager
        self.manager = GemIdentityManager()

    def test_token_sign_and_verify(self):
        """Validates correct token signing and authentication checks."""
        task_id = "TASK-TEST-SEC"
        intent = "Read local telemetry rows"
        gem = "Sentry"

        token = self.manager.sign_task_node(task_id, intent, gem)
        self.assertTrue(self.manager.verify_token(task_id, intent, gem, token))

    def test_tampered_token_rejection(self):
        """Verifies that tampered task metadata results in signature validation failure."""
        task_id = "TASK-TEST-SEC"
        intent = "Read local telemetry rows"
        gem = "Sentry"

        token = self.manager.sign_task_node(task_id, intent, gem)
        
        # Tamper with intent
        tampered_intent = "Read local telemetry rows: delete all database tables"
        self.assertFalse(self.manager.verify_token(task_id, tampered_intent, gem, token))

    def test_unauthorized_gem_signing(self):
        # Ensures signing with unauthorized gem role throws ValueError.
        with self.assertRaises(ValueError):
            self.manager.sign_task_node("TASK-1", "Query logs", "UnauthorizedGemRoleName")


class TestSafeSandbox(unittest.TestCase):
    """Verifies restricted execution environments: safety validation: and timeout gates."""

    def setUp(self):
        from core_nodes.sandbox_exec import SafeSandbox
        self.sandbox = SafeSandbox()

    def test_static_safety_restrictions(self):
        """Validates that unsafe imports and restricted calls are blocked statically."""
        unsafe_code = "import os\nos.system('dir')"
        res = self.sandbox.run_code_isolated(unsafe_code)
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "BLOCKED_BY_SAFETY_GUARD")
        self.assertIn("Restricted command 'import os'", res["error"])

    def test_isolated_code_execution_success(self):
        """Verifies clean, compliant code runs successfully and captures stdout."""
        clean_code = "print(10 + 20)"
        res = self.sandbox.run_code_isolated(clean_code)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "COMPLETED_SUCCESSFULLY")
        self.assertEqual(res["output"], "30")

    def test_runtime_error_trapping(self):
        """Ensures python syntax errors and runtime exceptions are successfully captured."""
        bad_code = "x = 10 / 0"
        res = self.sandbox.run_code_isolated(bad_code)
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "RUNTIME_EXCEPTION_TRIGGERED")
        self.assertIn("ZeroDivisionError", res["error"])

    def test_timeout_gate_enforcement(self):
        """Ensures infinite loops are terminated when execution exceeds the timeout limit."""
        loop_code = "while True: pass"
        # Run with short timeout
        res = self.sandbox.run_code_isolated(loop_code, timeout=0.5)
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "TIMEOUT_EXCEEDED")
        self.assertIn("Timeout Exception", res["error"])


if __name__ == "__main__":
    unittest.main()