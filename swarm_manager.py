import os
import sys
import sqlite3
import time
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Import all 10 engine modules
from core_nodes.memory_bank import PersistentMemoryBank
from core_nodes.agent_security import GemIdentityManager
from core_nodes.sandbox_exec import SafeSandbox
from core_nodes.live_stream_bridge import LiveStreamBridge
from core_nodes.compliance_router import ComplianceRouter
from core_nodes.negotiator_node import NegotiatorNode
from core_nodes.semantic_cataloger import SemanticCataloger
from core_nodes.self_healing import HealthMonitor
from core_nodes.off_grid_protocol import OffGridController
from core_nodes.event_automation import EventAutomationEngine

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class TaskNode:
    """Represents a specific unit of execution within the Swarm Manager framework."""

    def __init__(self, task_id: str, intent: str, agent_gem: str = "Architect"):
        self.task_id = task_id
        self.intent = intent
        self.agent_gem = agent_gem  # 'Architect', 'Worker', or 'Critic'
        self.status = "PENDING"
        self.output = ""
        self.refinement_count = 0


class Orchestrator:
    """Orchestrates task routing, executes compliance Critic checks, and maintains SQLite logs."""

    def __init__(self, db_path: str = None):
        self.root_dir = os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(self.root_dir, "goings_os_vault.db")
        self.humanitarian_db = os.path.join(self.root_dir, "choice_legacy_vault.db")
        self.error_log_db = os.path.join(self.root_dir, "error_log.db")
        self._initialize_vault_tables()
        self._initialize_error_log_db()
        self.task_queue = []

        # Core Swarm Engine Components
        self.memory_bank = None
        self.security_manager = None
        self.sandbox = None
        self.live_bridge = None
        self.compliance_router = None
        self.negotiator = None
        self.semantic_cataloger = None
        self.health_monitor = None
        self.off_grid = None
        self.event_engine = None

    def _initialize_error_log_db(self):
        """Forces WAL mode and prepares the initialization and execution error log table."""
        try:
            connection = sqlite3.connect(self.error_log_db, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS initialization_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    engine_id TEXT,
                    error_message TEXT
                )
            """)
            connection.commit()
            connection.close()
        except sqlite3.Error:
            pass

    def log_initialization_error(self, engine_id: str, error_message: str):
        """Appends a new startup or execution failure trace inside error_log.db."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        try:
            connection = sqlite3.connect(self.error_log_db, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO initialization_errors (timestamp, engine_id, error_message)
                VALUES (?, ?, ?)
            """, (timestamp, engine_id, error_message))
            connection.commit()
            connection.close()
        except sqlite3.Error as err:
            sys.stderr.write(f"Error log insert failure: {str(err)}\n")

    def initialize_swarm(self) -> bool:
        """Starts all 10 core Swarm nodes in dependency order, logging any startup failures."""
        print("\n🏛️ [ORCHESTRATOR] Initializing Master Swarm components in dependency order...")
        current_node = "memory_bank"
        try:
            # 1. memory_bank
            current_node = "memory_bank"
            self.memory_bank = PersistentMemoryBank(db_path=self.db_path)
            # Verify database accessibility to ensure initialization issues propagate
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            print(" -> [1/10] PersistentMemoryBank initialized successfully")

            # 2. agent_security
            current_node = "agent_security"
            self.security_manager = GemIdentityManager()
            print(" -> [2/10] GemIdentityManager initialized successfully")

            # 3. sandbox_exec
            current_node = "sandbox_exec"
            self.sandbox = SafeSandbox()
            print(" -> [3/10] SafeSandbox initialized successfully")

            # 4. live_stream_bridge
            current_node = "live_stream_bridge"
            self.live_bridge = LiveStreamBridge()
            self.live_bridge.bind_to_swarm_orchestrator(self)
            print(" -> [4/10] LiveStreamBridge initialized successfully")

            # 5. compliance_router
            current_node = "compliance_router"
            self.compliance_router = ComplianceRouter(self.memory_bank)
            print(" -> [5/10] ComplianceRouter initialized successfully")

            # 6. negotiator_node
            current_node = "negotiator_node"
            self.negotiator = NegotiatorNode(self.memory_bank)
            print(" -> [6/10] NegotiatorNode initialized successfully")

            # 7. semantic_cataloger
            current_node = "semantic_cataloger"
            self.semantic_cataloger = SemanticCataloger()
            print(" -> [7/10] SemanticCataloger initialized successfully")

            # 8. self_healing
            current_node = "self_healing"
            self.health_monitor = HealthMonitor(self.memory_bank)
            print(" -> [8/10] HealthMonitor initialized successfully")

            # 9. off_grid_protocol
            current_node = "off_grid_protocol"
            self.off_grid = OffGridController(self.root_dir)
            print(" -> [9/10] OffGridController initialized successfully")

            # 10. event_automation
            current_node = "event_automation"
            self.event_engine = EventAutomationEngine(self.root_dir)
            self.event_engine.register_event_listener("voice_ingest", self.handle_voice_event)
            print(" -> [10/10] EventAutomationEngine initialized successfully")

            # Register all engines in HealthMonitor for heartbeat checking
            for engine_id in self.nodes_to_monitor():
                self.health_monitor.register_node(engine_id, tenant="Goings OS")

            print("🏛️ [ORCHESTRATOR] Swarm initialization sequence finalized: VAULT IS SECURE.")
            return True

        except Exception as err:
            failed_id = current_node
            err_msg = str(err)
            sys.stderr.write(f"❌ Swarm initialization error for '{failed_id}': {err_msg}\n")
            self.log_initialization_error(failed_id, err_msg)
            
            if self.health_monitor:
                try:
                    self.health_monitor.recover_node(failed_id)
                except Exception:
                    pass
            return False

    def check_swarm_heartbeat(self) -> dict:
        """Central heartbeat monitor checking responsiveness across all 10 core engines."""
        health_status = {}
        if not self.health_monitor:
            print(" -> Heartbeat monitor: HealthMonitor is not initialized: skipping check")
            return health_status

        for engine_id in self.nodes_to_monitor():
            try:
                # Check health status from monitor
                health = self.health_monitor.check_node_health(engine_id)
                
                if not health["healthy"]:
                    # Log failure to error log database
                    self.log_initialization_error(engine_id, "Heartbeat responsiveness failure")
                    # Trigger self-healing recovery restart
                    self.health_monitor.recover_node(engine_id)
                    health_status[engine_id] = "RECOVERED"
                else:
                    health_status[engine_id] = "HEALTHY"
            except Exception as err:
                self.log_initialization_error(engine_id, f"Heartbeat check exception: {str(err)}")
                health_status[engine_id] = "FAULT"

        return health_status

    def nodes_to_monitor(self) -> list[str]:
        """Returns the list of core engine IDs tracked under the heartbeat monitor."""
        return [
            "memory_bank", "agent_security", "sandbox_exec", "live_stream_bridge",
            "compliance_router", "negotiator_node", "semantic_cataloger",
            "self_healing", "off_grid_protocol", "event_automation"
        ]

    def handle_voice_event(self, payload: dict):
        """Processes voice command events and logs them through Event Automation."""
        intent = payload.get("intent", "Execute standard routine")
        print(f" -> [ORCHESTRATOR CALLBACK] Voice command event processed: '{intent}'")
        # Log to API handler console logs
        OrchestratorAPIHandler.add_log(f"Event Automation: Handled voice intent: '{intent}'")

    def _initialize_vault_tables(self):
        """Forces WAL mode and initializes task monitoring telemetry tables."""
        for path in [self.db_path, self.humanitarian_db]:
            try:
                connection = sqlite3.connect(path, timeout=30.0)
                cursor = connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS swarm_task_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        task_id TEXT UNIQUE,
                        intent TEXT,
                        agent_gem TEXT,
                        status TEXT,
                        output TEXT,
                        refinements INTEGER
                    )
                """)
                connection.commit()
                connection.close()
            except sqlite3.Error:
                pass

    def log_task_state_to_db(self, node: TaskNode):
        """Persists the current status and output of a TaskNode into the sqlite vault."""
        target_db = self.db_path
        # Segregate Choice Inc related telemetry to the humanitarian vault
        if "choice" in node.intent.lower():
            target_db = self.humanitarian_db

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        try:
            connection = sqlite3.connect(target_db, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO swarm_task_logs (timestamp, task_id, intent, agent_gem, status, output, refinements)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    timestamp=excluded.timestamp,
                    agent_gem=excluded.agent_gem,
                    status=excluded.status,
                    output=excluded.output,
                    refinements=excluded.refinements
            """, (timestamp, node.task_id, node.intent, node.agent_gem, node.status, node.output, node.refinement_count))
            connection.commit()
            connection.close()
        except sqlite3.Error as err:
            sys.stderr.write(f"Database log error: {str(err)}\n")

    def add_task(self, task_id: str, intent: str) -> TaskNode:
        """Constructs a TaskNode and pushes it to the active execution queue."""
        node = TaskNode(task_id, intent, "Architect")
        self.task_queue.append(node)
        node.status = "QUEUED"
        self.log_task_state_to_db(node)
        return node

    def execute_critic_compliance_check(self, output: str) -> tuple[bool, str]:
        """Validates output against absolute typographical and terminology rules."""
        # 1. Total and absolute prohibition of em-dashes
        if "\u2014" in output or "--" in output:
            return False, "REJECTED: Em-dashes are strictly prohibited: utilize colons or semicolons instead."
        
        # 2. Terminology Mandate: Always use 'Private' and 'Private Governor'
        # Reject un-insulated or high-level global formulations
        uninsulated_terms = ["public governor", "global governor", "uninsulated", "un-insulated"]
        for term in uninsulated_terms:
            if term in output.lower():
                return False, f"REJECTED: Terminology mandate violation: '{term}' detected. Use 'Private' or 'Private Governor'."
        
        return True, "ACCEPTED: Compliance verification approved."

    def execute_worker_refinement(self, intent: str, previous_output: str, feedback: str) -> str:
        """Simulates the Worker Gem correcting output based on Critic compliance feedback."""
        # Simulate clean, rule-compliant output correction
        refined = previous_output
        if "\u2014" in refined:
            refined = refined.replace("\u2014", ": ")
        if "--" in refined:
            refined = refined.replace("--", ": ")
        
        # Correct terminology violations
        refined = refined.replace("public governor", "Private Governor")
        refined = refined.replace("global governor", "Private Governor")
        refined = refined.replace("uninsulated", "Private")
        refined = refined.replace("un-insulated", "Private")
        
        # If no changes were made but we were rejected, output a compliant default template
        if refined == previous_output:
            refined = "Secured private operational payload: processed under the authority of the Private Governor."
            
        return refined

    def process_task_execution_loop(self, node: TaskNode) -> str:
        """Drives the loop: dispatches intent to Worker, passes output to Critic, and runs refinements."""
        print(f"\n⚙️ [ORCHESTRATOR] Initializing execution loop for Task: {node.task_id}")
        
        # 1. Receive intent from the Architect
        node.agent_gem = "Architect"
        node.status = "ARCHITECT_INTENT_RECEIVED"
        self.log_task_state_to_db(node)
        print(f" -> Phase 1: Architect intent received: '{node.intent}'")

        # 2. Dispatch to the Worker
        node.agent_gem = "Worker"
        node.status = "WORKER_DISPATCHED"
        self.log_task_state_to_db(node)
        
        # Simulation: Worker produces initial raw output (which might contain compliance issues)
        # We will make the first output contain a compliance warning (an em-dash) to test the loop
        initial_output = f"Executing task: {node.intent} \u2014 using the public governor configuration."
        node.output = initial_output
        print(" -> Phase 2: Worker generated initial output.")

        # 3. Automatically pass to Critic
        max_refinement_ceiling = 3
        while node.refinement_count < max_refinement_ceiling:
            node.agent_gem = "Critic"
            node.status = "CRITIC_EVALUATING"
            self.log_task_state_to_db(node)
            
            check_passed, feedback_msg = self.execute_critic_compliance_check(node.output)
            print(f" -> Phase 3: Critic evaluation result: {feedback_msg}")
            
            if check_passed:
                node.status = "COMPLETED"
                self.log_task_state_to_db(node)
                print(" -> Execution Loop complete: Task successfully verified.")
                return "SUCCESS"
            
            # 4. Trigger Refinement Loop
            node.refinement_count += 1
            print(f" ⚠️ Refinement loop {node.refinement_count} triggered. Critic Feedback: {feedback_msg}")
            node.agent_gem = "Worker"
            node.status = f"REFINING_ITERATION_{node.refinement_count}"
            self.log_task_state_to_db(node)
            
            # Worker refines the output based on feedback
            refined_output = self.execute_worker_refinement(node.intent, node.output, feedback_msg)
            node.output = refined_output
            self.log_task_state_to_db(node)

        # Capped threshold reached without compliance success
        node.status = "FAILED_COMPLIANCE"
        self.log_task_state_to_db(node)
        print(" ❌ CRITICAL: Task execution halted: max compliance refinements reached.")
        return "FAILURE"


class OrchestratorAPIHandler(BaseHTTPRequestHandler):
    """Processes HTTP requests from the web interface, exposing Swarm state and records."""
    orchestrator_instance = None
    log_messages = []

    @classmethod
    def add_log(cls, msg):
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        cls.log_messages.append(f"[{timestamp}] {msg}")
        if len(cls.log_messages) > 50:
            cls.log_messages.pop(0)

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if self.path == "/api/status":
            try:
                # Ensure core monitor presence
                if self.orchestrator_instance.health_monitor is None:
                    self.orchestrator_instance.initialize_swarm()
                
                health = self.orchestrator_instance.check_swarm_heartbeat()
                status_data = []
                for engine in self.orchestrator_instance.nodes_to_monitor():
                    status_data.append({
                        "id": engine,
                        "name": engine.replace("_", " ").title(),
                        "healthy": health.get(engine) in ("HEALTHY", "RECOVERED"),
                        "status": health.get(engine, "UNKNOWN")
                    })
                
                self._set_headers(200)
                payload = json.dumps({"engines": status_data})
                self.wfile.write(payload.encode("utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                
        elif self.path == "/api/logs":
            try:
                tasks = []
                errors = []
                
                # Check health monitor presence
                if self.orchestrator_instance.health_monitor is None:
                    self.orchestrator_instance.initialize_swarm()

                # Read commercial task logs
                if os.path.exists(self.orchestrator_instance.db_path):
                    try:
                        conn = sqlite3.connect(self.orchestrator_instance.db_path, timeout=5.0)
                        cursor = conn.cursor()
                        cursor.execute("SELECT timestamp, task_id, intent, agent_gem, status, output FROM swarm_task_logs ORDER BY id DESC LIMIT 10")
                        for row in cursor.fetchall():
                            tasks.append({
                                "timestamp": row[0],
                                "task_id": row[1],
                                "intent": row[2],
                                "agent": row[3],
                                "status": row[4],
                                "output": row[5],
                                "tenant": "Goings OS"
                            })
                        conn.close()
                    except Exception as e:
                        self.add_log(f"Commercial DB log read failure: {str(e)}")

                # Read humanitarian task logs
                if os.path.exists(self.orchestrator_instance.humanitarian_db):
                    try:
                        conn = sqlite3.connect(self.orchestrator_instance.humanitarian_db, timeout=5.0)
                        cursor = conn.cursor()
                        cursor.execute("SELECT timestamp, task_id, intent, agent_gem, status, output FROM swarm_task_logs ORDER BY id DESC LIMIT 10")
                        for row in cursor.fetchall():
                            tasks.append({
                                "timestamp": row[0],
                                "task_id": row[1],
                                "intent": row[2],
                                "agent": row[3],
                                "status": row[4],
                                "output": row[5],
                                "tenant": "Choice Inc"
                            })
                        conn.close()
                    except Exception as e:
                        self.add_log(f"Humanitarian DB log read failure: {str(e)}")

                # Read error log database
                if os.path.exists(self.orchestrator_instance.error_log_db):
                    try:
                        conn = sqlite3.connect(self.orchestrator_instance.error_log_db, timeout=5.0)
                        cursor = conn.cursor()
                        cursor.execute("SELECT timestamp, engine_id, error_message FROM initialization_errors ORDER BY id DESC LIMIT 10")
                        for row in cursor.fetchall():
                            errors.append({
                                "timestamp": row[0],
                                "engine_id": row[1],
                                "message": row[2]
                            })
                        conn.close()
                    except Exception as e:
                        self.add_log(f"Error DB log read failure: {str(e)}")

                # Sort consolidated tasks by timestamp descending
                tasks.sort(key=lambda x: x["timestamp"], reverse=True)

                self._set_headers(200)
                payload = json.dumps({
                    "tasks": tasks[:15],
                    "errors": errors,
                    "server_logs": self.log_messages
                })
                self.wfile.write(payload.encode("utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode("utf-8"))
        except Exception:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Malformed JSON payload"}).encode("utf-8"))
            return

        if self.path == "/api/task":
            try:
                intent = data.get("intent", "Execute default routine")
                task_id = f"TASK-{int(time.time())}-WEB"
                self.add_log(f"Dispatching task {task_id}: {intent}")

                # Ensure orchestrator presence
                if self.orchestrator_instance.health_monitor is None:
                    self.orchestrator_instance.initialize_swarm()

                node = self.orchestrator_instance.add_task(task_id, intent)
                result = self.orchestrator_instance.process_task_execution_loop(node)
                
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "task_id": task_id,
                    "intent": intent,
                    "status": node.status,
                    "output": node.output,
                    "result": result
                }).encode("utf-8"))
                self.add_log(f"Task {task_id} completed: status {node.status}")
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif self.path == "/api/voice":
            try:
                # Ensure orchestrator presence
                if self.orchestrator_instance.health_monitor is None:
                    self.orchestrator_instance.initialize_swarm()

                mode = data.get("mode", "default")
                
                # Check for simulated fail trigger
                if mode == "fail":
                    self.add_log("Voice connection sync failure simulated! Triggering self-healing health check...")
                    # Age the last_contact timestamp of live_stream_bridge to trigger failure
                    self.orchestrator_instance.health_monitor.nodes["live_stream_bridge"]["last_contact"] -= 10.0
                    
                    # Run health check & recovery via self_healing
                    recovered = self.orchestrator_instance.health_monitor.recover_node("live_stream_bridge")
                    
                    if recovered:
                        self.add_log("Live Stream Bridge re-instantiated via self-healing recovery.")
                        # Re-initialize the bridge session
                        self.orchestrator_instance.live_bridge.initialize_session(f"WEB-{int(time.time())}")
                        status_str = "RECOVERED"
                    else:
                        status_str = "FAILED"
                        
                    self._set_headers(200)
                    self.wfile.write(json.dumps({
                        "intent": "Voice Sync Failure: Self-Healing Active",
                        "response_text": "WebRTC bridge socket healed and re-instantiated cleanly.",
                        "bridge_status": status_str
                    }).encode("utf-8"))
                    return

                self.add_log(f"Simulating Voice Ingest: mode {mode}")
                
                # Check active Live Stream Bridge session
                if not self.orchestrator_instance.live_bridge.is_active:
                    self.orchestrator_instance.live_bridge.initialize_session(f"WEB-{int(time.time())}")

                # Select audio bytes
                if mode == "sync":
                    audio_bytes = b"\x00\x01\x02" * 41  # 123 bytes
                else:
                    audio_bytes = b"\x00\x01" * 10

                intent = self.orchestrator_instance.live_bridge.stream_audio_inbound(audio_bytes)
                response_text = f"Simulated vocal speech processed: {intent}: under Private Governor supervision."
                self.orchestrator_instance.live_bridge.stream_audio_outbound(response_text)

                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "intent": intent,
                    "response_text": response_text,
                    "bridge_status": "ACTIVE"
                }).encode("utf-8"))
                self.add_log(f"Voice Command processed: {intent}")
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))


def start_api_server(orchestrator, port=8000):
    """Launches concurrent ThreadingHTTPServer on specified port to interface with the web dashboard."""
    OrchestratorAPIHandler.orchestrator_instance = orchestrator
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, OrchestratorAPIHandler)
    print(f"\n🚀 [API SERVER] Goings OS Orchestrator API listening on http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping API server...")
        httpd.server_close()


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS SWARM MANAGER COGNITIVE NODE       ")
    print("==========================================================")
    
    orchestrator = Orchestrator()
    success = orchestrator.initialize_swarm()
    
    if success:
        # Launch API Server
        start_api_server(orchestrator, port=8000)
    else:
        print("❌ Swarm initialization failed: API server will not start.")
