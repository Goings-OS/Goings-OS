# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: CORE SWARM STRESS TESTING & CONCURRENCY QUALITY ASSURANCE
# COMPLIANCE: ZERO EM-DASHES; STANDARD UNITTEST ALIGNMENT
# ==============================================================================

import os
import sqlite3
import sys
import unittest
import json

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
        ok, msg = self.orchestrator.execute_critic_compliance_check("Compliance payload \u2014 invalid.")
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
        self.assertNotIn("\u2014", node.output)
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


class TestLiveStreamBridge(unittest.TestCase):
    """Verifies low-latency media sessions: bidirectional packet streaming: and orchestrator bindings."""

    def setUp(self):
        from core_nodes.live_stream_bridge import LiveStreamBridge
        from swarm_manager import Orchestrator
        self.bridge = LiveStreamBridge()
        self.orchestrator = Orchestrator()

    def test_session_management(self):
        """Validates socket allocation and clean termination behaviors."""
        self.assertTrue(self.bridge.initialize_session("TEST-SESS-99"))
        self.assertTrue(self.bridge.is_active)
        self.assertEqual(self.bridge.session_id, "TEST-SESS-99")
        
        self.assertTrue(self.bridge.terminate_session())
        self.assertFalse(self.bridge.is_active)
        self.assertIsNone(self.bridge.session_id)

    def test_bidirectional_audio_synthesis(self):
        """Verifies low-latency Speech-to-Text parsing and Text-to-Speech outbound packet generation."""
        self.bridge.initialize_session("TEST-SESS-99")
        
        # Test Inbound STT Conversion
        command = self.bridge.stream_audio_inbound(b"\x00" * 123)
        self.assertEqual(command, "Vocal Command: Sync Choice grant database")

        # Test Outbound TTS conversion
        audio_packet = self.bridge.stream_audio_outbound("Cognitive validation complete.")
        self.assertIsNotNone(audio_packet)
        self.assertEqual(audio_packet, "Cognitive validation complete.".encode("utf-8"))

    def test_orchestrator_binding(self):
        """Validates that incoming voice streams successfully trigger Swarm Manager pipelines."""
        self.bridge.initialize_session("TEST-SESS-99")
        self.bridge.bind_to_swarm_orchestrator(self.orchestrator)
        
        # Ingesting command should trigger tasks in swarm
        # First check that task queue is empty
        self.orchestrator.task_queue.clear()
        
        self.bridge.stream_audio_inbound(b"\x00" * 123)
        self.assertEqual(len(self.orchestrator.task_queue), 1)
        self.assertEqual(self.orchestrator.task_queue[0].intent, "Vocal Command: Sync Choice grant database")
        self.assertEqual(self.orchestrator.task_queue[0].status, "COMPLETED")


class TestComplianceRouter(unittest.TestCase):
    """Verifies that the logical firewall correctly routes and logs decisions based on corporate rules."""

    def setUp(self):
        from core_nodes.compliance_router import ComplianceRouter
        self.router = ComplianceRouter()

    def test_compliant_payload(self):
        """Verifies that fully compliant payloads are routed directly to the output layer."""
        output = "Secured private operational payload: processed under the authority of the Private Governor."
        dest = self.router.route_task_output("TEST-TASK-001", output)
        self.assertEqual(dest, "OUTPUT_LAYER")

    def test_em_dash_violation(self):
        """Checks that outputs containing em-dashes fail verification and route to the Governor."""
        output = "Processing task output \u2014 utilizing the default settings."
        dest = self.router.route_task_output("TEST-TASK-002", output)
        self.assertEqual(dest, "GOVERNOR")

    def test_terminology_violation(self):
        """Checks that prohibited high-level/global terms trigger fallback routing."""
        output = "Deploying output to the global governor portal."
        dest = self.router.route_task_output("TEST-TASK-003", output)
        self.assertEqual(dest, "GOVERNOR")

    def test_shareholder_distribution_violation(self):
        """Ensures shareholder distributions must be designated as owner's draw allocations."""
        # Failing case: mentions shareholder distribution but NOT owner's draw
        output_fail = "Logging a shareholder distribution of $3,000.00."
        dest_fail = self.router.route_task_output("TEST-TASK-004", output_fail)
        self.assertEqual(dest_fail, "GOVERNOR")

        # Passing case: mentions shareholder distribution designated as owner's draw
        output_pass = "Logging a shareholder distribution tracked as an owner's draw allocation."
        dest_pass = self.router.route_task_output("TEST-TASK-005", output_pass)
        self.assertEqual(dest_pass, "OUTPUT_LAYER")

    def test_cruise_capacity_violation(self):
        """Ensures Norfolk Takeover Cruise stateroom capacity limit of 400 is not exceeded."""
        output = "Norfolk Takeover Cruise schedule set: manifest capacity is 450 staterooms."
        dest = self.router.route_task_output("TEST-TASK-006", output)
        self.assertEqual(dest, "GOVERNOR")

        # Verify structured metadata check
        metadata = {"cruise_capacity": 401, "is_cruise_related": True}
        dest_meta = self.router.route_task_output("TEST-TASK-007", "Norfolk Takeover Cruise update.", metadata)
        self.assertEqual(dest_meta, "GOVERNOR")

    def test_cruise_deposit_and_commission_violations(self):
        """Checks base deposit is exactly $150 and non-refundable, and broker split is exactly $75."""
        # Failing case: refundable deposit
        output_fail1 = "Norfolk Cruise client deposit of $150.00 is fully refundable."
        dest_fail1 = self.router.route_task_output("TEST-TASK-008", output_fail1)
        self.assertEqual(dest_fail1, "GOVERNOR")

        # Failing case: incorrect deposit amount
        output_fail2 = "Norfolk Cruise non-refundable client deposit of $120.00."
        dest_fail2 = self.router.route_task_output("TEST-TASK-009", output_fail2)
        self.assertEqual(dest_fail2, "GOVERNOR")

        # Failing case: incorrect broker commission split
        output_fail3 = "Norfolk Cruise non-refundable deposit is $150.00: broker commission split is $80.00."
        dest_fail3 = self.router.route_task_output("TEST-TASK-010", output_fail3)
        self.assertEqual(dest_fail3, "GOVERNOR")

        # Compliant cruise case
        output_pass = "Norfolk Cruise non-refundable base client deposit: $150.00: broker commission split: $75.00: capacity: 380 souls."
        dest_pass = self.router.route_task_output("TEST-TASK-011", output_pass)
        self.assertEqual(dest_pass, "OUTPUT_LAYER")

    def test_revenue_floor_violations(self):
        """Validates that weekly revenue floor of $5,000 and daily operational yield of $714.28 are enforced."""
        # Weekly revenue floor fail
        metadata_week = {"weekly_revenue": 4500.00}
        dest_week = self.router.route_task_output("TEST-TASK-012", "Weekly projection report", metadata_week)
        self.assertEqual(dest_week, "GOVERNOR")

        # Daily yield benchmark fail
        metadata_daily = {"daily_yield": 700.00}
        dest_daily = self.router.route_task_output("TEST-TASK-013", "Daily operational yield report", metadata_daily)
        self.assertEqual(dest_daily, "GOVERNOR")

        # Compliant benchmarks
        metadata_ok = {"weekly_revenue": 5500.00, "daily_yield": 750.00}
        dest_ok = self.router.route_task_output("TEST-TASK-014", "Operational report", metadata_ok)
        self.assertEqual(dest_ok, "OUTPUT_LAYER")

    def test_sqlite_memory_bank_logging(self):
        """Confirms compliance decisions are correctly logged and isolated in the SQLite vaults."""
        task_id = "TEST-CHOICE-ROUTING-LOG-99"
        # Since it's choice related, it must go to the choice legacy database
        output = "Choice Inc philanthropic allocation: Weekly revenue floor: $6,000.00: daily yield: $800.00."
        dest = self.router.route_task_output(task_id, output)
        self.assertEqual(dest, "OUTPUT_LAYER")

        # Retrieve logged context from Memory Bank
        records = self.router.memory_bank.retrieve_context({"task_id": task_id}, tenant="Choice Inc")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["context_key"], f"COMPLIANCE_ROUTING_{task_id}")
        self.assertEqual(records[0]["context_value"], "Status: APPROVED")
        self.assertTrue(records[0]["metadata"]["is_compliant"])


class TestNegotiatorNode(unittest.TestCase):
    """Verifies autonomous negotiation, tool registry management, and key-filtering logs."""

    def setUp(self):
        from core_nodes.negotiator_node import NegotiatorNode, CredentialVault
        self.vault = CredentialVault()
        self.vault.store_credential("TEST_API_KEY", "secret_pass_token_999")
        self.vault.store_credential("SENSITIVE_RESP", "response_secret_hash_888")
        
        self.node = NegotiatorNode(vault=self.vault)
        
        # Clear database records for cleaner isolation queries
        for db in [self.node.memory_bank.db_path, self.node.memory_bank.humanitarian_db]:
            if os.path.exists(db):
                import sqlite3
                conn = sqlite3.connect(db)
                conn.execute("DELETE FROM session_memory_cache WHERE context_key LIKE 'NEGOTIATION_%'")
                conn.commit()
                conn.close()

        def dummy_handler(payload):
            key = payload.get("auth_key")
            if key != "secret_pass_token_999":
                raise ValueError("Unauthorized client")
            return {
                "status": "success",
                "secret_token": "response_secret_hash_888",
                "data": "Authorized data output"
            }
            
        self.node.register_tool("dummy_endpoint", dummy_handler)

    def test_tool_registration(self):
        """Verifies registered integration tools exist with matching details."""
        self.assertIn("dummy_endpoint", self.node.tools)
        self.assertIsNotNone(self.node.tools["dummy_endpoint"]["handler"])

    def test_execute_negotiation_success(self):
        """Verifies a successful negotiation run and parsed redacted payload output."""
        payload = {"auth_key": "vault://TEST_API_KEY", "sync_type": "full"}
        res = self.node.execute_negotiation("Sync database", "dummy_endpoint", payload)
        
        self.assertTrue(res["success"])
        self.assertEqual(res["response"]["secret_token"], "[REDACTED_SECURE_VALUE]")
        self.assertEqual(res["response"]["status"], "success")

    def test_execute_negotiation_failure(self):
        """Checks exception tracking for failed or unauthorized negotiation runs."""
        payload = {"auth_key": "wrong_key", "sync_type": "incremental"}
        res = self.node.execute_negotiation("Sync database", "dummy_endpoint", payload)
        
        self.assertFalse(res["success"])
        self.assertIsNone(res["response"])
        self.assertEqual(res["error"], "Unauthorized client")

    def test_credential_redaction(self):
        """Validates that no plain-text credentials leak into logged request or response payloads."""
        payload = {"auth_key": "vault://TEST_API_KEY", "client_password": "super_secret_value"}
        
        # Register the raw client password in the vault so the string scanner can catch it
        self.vault.store_credential("PASSWORD", "super_secret_value")
        
        res = self.node.execute_negotiation("Sync database", "dummy_endpoint", payload)
        self.assertTrue(res["success"])

        # Verify the logged payload has redacted keys
        records = self.node.memory_bank.retrieve_context({"objective": "Sync database"}, tenant="Goings OS")
        self.assertEqual(len(records), 1)
        
        metadata = records[0]["metadata"]
        # Verify request parameters are sanitized
        self.assertEqual(metadata["request_payload"]["auth_key"], "[REDACTED_SECURE_VALUE]")
        self.assertEqual(metadata["request_payload"]["client_password"], "[REDACTED_SECURE_VALUE]")
        # Verify response parameters are sanitized
        self.assertEqual(metadata["response_payload"]["secret_token"], "[REDACTED_SECURE_VALUE]")
        
        # Ensure raw key strings do not exist in plain-text metadata representation
        metadata_str = json.dumps(metadata)
        self.assertNotIn("secret_pass_token_999", metadata_str)
        self.assertNotIn("response_secret_hash_888", metadata_str)
        self.assertNotIn("super_secret_value", metadata_str)


class TestSemanticCataloger(unittest.TestCase):
    """Verifies recursive crawler indexing, MD5 content checks, and semantic similarity search queries."""

    def setUp(self):
        import tempfile
        from core_nodes.semantic_cataloger import SemanticCataloger
        
        # Setup temporary directories and database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_manifest.db")
        self.cataloger = SemanticCataloger(db_path=self.db_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def test_database_initialization(self):
        """Validates schema provisioning and WAL journal enforcement on catalog_manifest."""
        self.assertTrue(os.path.exists(self.db_path))
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal")

    def test_embedding_normalization_and_similarity(self):
        """Verifies vector unit length and cosine similarity calculations."""
        text = "This is a low-latency WebRTC live stream socket connection."
        vector = self.cataloger.generate_embeddings(text)
        self.assertEqual(len(vector), 128)
        
        # Verify L2 normalization
        magnitude = sum(x * x for x in vector) ** 0.5
        self.assertAlmostEqual(magnitude, 1.0, places=5)
        
        # Test similarity dot products
        vec_query = self.cataloger.generate_embeddings("WebRTC stream socket")
        vec_doc1 = self.cataloger.generate_embeddings("WebRTC stream socket capture connection")
        vec_doc2 = self.cataloger.generate_embeddings("Completely unrelated financial ledger allocation")
        
        sim1 = sum(q * d for q, d in zip(vec_query, vec_doc1))
        sim2 = sum(q * d for q, d in zip(vec_query, vec_doc2))
        
        # Matching document must score higher
        self.assertGreater(sim1, sim2)

    def test_incremental_workspace_indexing(self):
        """Verifies file scanning, MD5 hash calculation, and incremental skips."""
        file_path = os.path.join(self.test_dir, "test_document.md")
        
        # Create test document
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Keep It Goings Consulting: Private Governor integration.")
            
        # First index pass
        self.cataloger.index_workspace(self.test_dir)
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        rows_initial = conn.execute("SELECT file_path, content_hash FROM workspace_index").fetchall()
        self.assertEqual(len(rows_initial), 1)
        self.assertEqual(rows_initial[0][0], file_path)
        initial_hash = rows_initial[0][1]
        
        # Modify file and re-index
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Keep It Goings Consulting: Private Governor integration: updated database line.")
            
        self.cataloger.index_workspace(self.test_dir)
        rows_updated = conn.execute("SELECT file_path, content_hash FROM workspace_index").fetchall()
        self.assertEqual(len(rows_updated), 1)
        self.assertNotEqual(rows_updated[0][1], initial_hash)
        conn.close()

    def test_query_graph_retrieval(self):
        """Validates sorted relevance scores and query result thresholds."""
        # Create mock document records in manifest
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        
        doc1_vector = self.cataloger.generate_embeddings("Orchestrator Task Loop Worker")
        doc2_vector = self.cataloger.generate_embeddings("Choice Inc non-profit grant ledgers")
        
        conn.execute("""
            INSERT INTO workspace_index (file_path, content_hash, content, embedding_json, last_indexed)
            VALUES (?, ?, ?, ?, ?)
        """, ("doc1.md", "hash1", "Orchestrator Task Loop Worker", json.dumps(doc1_vector), "2026-06-16"))
        
        conn.execute("""
            INSERT INTO workspace_index (file_path, content_hash, content, embedding_json, last_indexed)
            VALUES (?, ?, ?, ?, ?)
        """, ("doc2.md", "hash2", "Choice Inc non-profit grant ledgers", json.dumps(doc2_vector), "2026-06-16"))
        
        conn.commit()
        conn.close()
        
        # Query for Orchestrator matches
        results = self.cataloger.query_graph("Worker task loop orchestrator", top_k=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["file_path"], "doc1.md")
        self.assertGreater(results[0]["similarity"], results[1]["similarity"])


if __name__ == "__main__":
    unittest.main()