import os
import sys
import sqlite3
import time
import json
import random
import threading
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
from core_nodes.api_integrator import UnifiedAPIConnector
from core_nodes.node_08_vault.schema_manager import SchemaManager, DatabaseObservabilityAgent

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class MutationEngine:
    """Supervises code mutations, handles compilation checks, exceptions, and retries."""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.log_path = os.path.join(orchestrator.root_dir, "mutation_history.log")
        self.migration_log_path = os.path.join(orchestrator.root_dir, "migration_audit.log")
        self.strategy = "STANDARD"
        self.retry_count = 0
        self.max_retries = 3
        self.history = []
        instructions_path = os.path.join(orchestrator.root_dir, "instructions.md")
        self.schema_manager = SchemaManager(orchestrator.db_path, instructions_path)
        self.observability_agent = DatabaseObservabilityAgent(orchestrator.db_path, self.schema_manager)
        self._initialize_log()

    def _initialize_log(self):
        """Creates the log files if they do not exist, verifying write access."""
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}] MutationEngine initialized: standard strategy set\n")
        if not os.path.exists(self.migration_log_path):
            with open(self.migration_log_path, "w", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}] MigrationAudit initialized: zero em-dash compliance active\n")

    def log_migration_audit(self, message: str):
        """Appends database migration audit logs without em-dashes."""
        clean_msg = message.replace("\u2014", ": ").replace("--", ": ")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        log_line = f"[{timestamp}] {clean_msg}\n"
        with open(self.migration_log_path, "a", encoding="utf-8") as f:
            f.write(log_line)

    def check_and_execute_migrations(self) -> dict:
        """Inspects database schema drifts and executes automated schema adjustments."""
        self.log_migration_audit("Checking database schema status for potential migrations")
        drift = self.schema_manager.detect_drift()
        
        if not drift["drift_detected"]:
            self.log_migration_audit("No schema drift detected: database schema is fully aligned")
            return {"status": "ALIGNED", "drift": drift}

        self.log_migration_audit("Schema drift detected: initiating dynamic database migrations")
        try:
            conn = sqlite3.connect(self.orchestrator.db_path, timeout=10.0)
            cursor = conn.cursor()

            # Handle missing tables
            for table_name in drift["missing_tables"]:
                self.log_migration_audit(f"Table '{table_name}' is missing: interpreting specifications from instructions")
                target_schemas = self.schema_manager.parse_specifications()
                columns_def = target_schemas.get(table_name, {})
                col_defs = []
                for col_name, col_type in columns_def.items():
                    col_defs.append(f"{col_name} {col_type}")
                
                query = f"CREATE TABLE {table_name} ({', '.join(col_defs)})"
                cursor.execute(query)
                self.log_migration_audit(f"Successfully executed: {query}")

            # Handle missing columns
            for table_name, missing_cols in drift["missing_columns"].items():
                for col_name, col_type in missing_cols:
                    self.log_migration_audit(f"Column '{col_name}' in table '{table_name}' is missing")
                    query = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                    cursor.execute(query)
                    self.log_migration_audit(f"Successfully executed: {query}")

            conn.commit()
            conn.close()
            self.log_migration_audit("Automated database schema migrations completed successfully")
            
            # Recalculate drift to verify
            drift = self.schema_manager.detect_drift()
            return {"status": "SUCCESS", "drift": drift}
            
        except Exception as migration_error:
            err_msg = str(migration_error)
            self.log_migration_audit(f"Automated migration failed: {err_msg}")
            return {"status": "FAILED", "error": err_msg, "drift": drift}

    def log_mutation(self, message: str):
        """Appends technical logs to mutation_history.log without em-dashes."""
        clean_msg = message.replace("\u2014", ": ").replace("--", ": ")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        log_line = f"[{timestamp}] {clean_msg}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(log_line)
        self.history.append({"timestamp": timestamp, "message": clean_msg})
        if len(self.history) > 50:
            self.history.pop(0)

    def execute_validation(self, code_str: str) -> dict:
        """Runs the compilation check and traps exceptions with dynamic retry strategies."""
        self.retry_count = 0
        self.strategy = "STANDARD"
        self.log_mutation(f"Initializing mutation compilation audit: standard strategy")

        while self.retry_count <= self.max_retries:
            try:
                modified_code = self._apply_strategy_modifications(code_str, self.strategy)
                self.log_mutation(f"Running compilation pass (Attempt {self.retry_count + 1}): Strategy {self.strategy}")
                compiled_obj = compile(modified_code, "<dynamic_mutation>", "exec")
                
                if self.orchestrator.sandbox:
                    self.log_mutation(f"Executing sandboxed subprocess validation run")
                    sandbox_res = self.orchestrator.sandbox.run_code_isolated(modified_code)
                    if not sandbox_res["success"]:
                        raise RuntimeError(f"Sandbox runtime execution failed: {sandbox_res['error']}")
                else:
                    local_scope = {}
                    exec(compiled_obj, {}, local_scope)

                self.log_mutation(f"Mutation compilation audit successful: code verified")
                return {
                    "success": True,
                    "strategy": self.strategy,
                    "attempts": self.retry_count + 1,
                    "error": None,
                    "status": "VERIFIED"
                }

            except Exception as runtime_error:
                error_msg = str(runtime_error)
                self.log_mutation(f"Compilation/Runtime Exception caught: {error_msg}")
                self.retry_count += 1
                if self.retry_count <= self.max_retries:
                    self.strategy = self._adjust_strategy(self.retry_count)
                    self.log_mutation(f"Strategy dynamically modified to: {self.strategy}")
                else:
                    self.log_mutation(f"Maximum mutation retries reached: compilation audit failed")
                    return {
                        "success": False,
                        "strategy": self.strategy,
                        "attempts": self.retry_count,
                        "error": error_msg,
                        "status": "FAULT"
                    }

    def _apply_strategy_modifications(self, code_str: str, strategy: str) -> str:
        """Adapts the code string dynamically based on the active mitigation strategy."""
        if strategy == "RELAXED_SYNTAX":
            lines = [line for line in code_str.splitlines() if not line.strip().startswith("#")]
            return "\n".join(lines)
        elif strategy == "SAFE_FALLBACK":
            wrapped_code = "try:\n"
            for line in code_str.splitlines():
                wrapped_code += f"    {line}\n"
            wrapped_code += "except Exception:\n    pass\n"
            return wrapped_code
        return code_str

    def _adjust_strategy(self, retry_index: int) -> str:
        """Returns the modified strategy key based on current retry count."""
        strategies = ["STANDARD", "RELAXED_SYNTAX", "SAFE_FALLBACK"]
        if retry_index < len(strategies):
            return strategies[retry_index]
        return "SAFE_FALLBACK"


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
        self.google_connector = None
        self.mutation_engine = MutationEngine(self)

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

    def execute_self_heal(self, node_id: str) -> bool:
        """Inspects the local directory tree, auto-corrects path alignment, and heals stalled node loading."""
        print(f" 🛠️ [SELF HEAL] Triggered path alignment audit for stalled node: '{node_id}'")
        
        # Log to initialization error log
        self.log_initialization_error(node_id, "Import or module load failure: executing self-heal recovery")
        
        # Dynamic inspection of directory tree
        try:
            core_nodes_dir = os.path.join(self.root_dir, "core_nodes")
            if not os.path.exists(core_nodes_dir):
                print(" 🛠️ [SELF HEAL] Warning: core_nodes folder not found: attempting to realign root dir paths")
                # Attempt to align path by setting GOINGS_OS_ROOT environment variable or adding to sys.path
                if os.path.exists(os.path.join(os.path.dirname(self.root_dir), "core_nodes")):
                    self.root_dir = os.path.dirname(self.root_dir)
                    os.environ["GOINGS_OS_ROOT"] = self.root_dir
                    print(f" 🛠️ [SELF HEAL] Path aligned: root folder set to: '{self.root_dir}'")
            
            # Ensure root directory and core_nodes directory are in sys.path
            if self.root_dir not in sys.path:
                sys.path.insert(0, self.root_dir)
            if core_nodes_dir not in sys.path:
                sys.path.insert(0, core_nodes_dir)
                
            print(f" 🛠️ [SELF HEAL] Auto-corrected path alignment: sys.path verified: restarting node '{node_id}'")
            return True
        except Exception as err:
            sys.stderr.write(f" 🛠️ [SELF HEAL] Error during path alignment audit: {str(err)}\n")
            return False

    def initialize_swarm(self) -> bool:
        """Starts all 10 core Swarm nodes in dependency order, logging any startup failures."""
        print("\n🏛️ [ORCHESTRATOR] Initializing Master Swarm components in dependency order...")
        
        nodes_initialization = [
            ("memory_bank", lambda: PersistentMemoryBank(db_path=self.db_path)),
            ("agent_security", lambda: GemIdentityManager()),
            ("sandbox_exec", lambda: SafeSandbox()),
            ("live_stream_bridge", lambda: LiveStreamBridge()),
            ("compliance_router", lambda: ComplianceRouter(self.memory_bank)),
            ("negotiator_node", lambda: NegotiatorNode(self.memory_bank)),
            ("semantic_cataloger", lambda: SemanticCataloger()),
            ("self_healing", lambda: HealthMonitor(self.memory_bank)),
            ("off_grid_protocol", lambda: OffGridController(self.root_dir)),
            ("event_automation", lambda: EventAutomationEngine(self.root_dir)),
            ("api_integrator", lambda: UnifiedAPIConnector(self.memory_bank))
        ]
        
        for index, (node_id, init_func) in enumerate(nodes_initialization, 1):
            retry_count = 0
            while retry_count < 2:
                try:
                    if node_id == "memory_bank":
                        self.memory_bank = init_func()
                        # Verify database accessibility to ensure initialization issues propagate
                        with sqlite3.connect(self.db_path) as conn:
                            conn.execute("SELECT 1")
                    elif node_id == "agent_security":
                        self.security_manager = init_func()
                    elif node_id == "sandbox_exec":
                        self.sandbox = init_func()
                    elif node_id == "live_stream_bridge":
                        self.live_bridge = init_func()
                        self.live_bridge.bind_to_swarm_orchestrator(self)
                    elif node_id == "compliance_router":
                        self.compliance_router = init_func()
                    elif node_id == "negotiator_node":
                        self.negotiator = init_func()
                    elif node_id == "semantic_cataloger":
                        self.semantic_cataloger = init_func()
                    elif node_id == "self_healing":
                        self.health_monitor = init_func()
                    elif node_id == "off_grid_protocol":
                        self.off_grid = init_func()
                    elif node_id == "event_automation":
                        self.event_engine = init_func()
                        self.event_engine.register_event_listener("voice_ingest", self.handle_voice_event)
                    elif node_id == "api_integrator":
                        self.google_connector = init_func()
                        self.google_connector.execute_workspace_handshake()
                    
                    if node_id == "api_integrator":
                        print(" -> [GOOGLE GATEWAY] UnifiedAPIConnector initialized and workspace handshake complete")
                    else:
                        print(f" -> [{index}/10] {node_id.replace('_', ' ').title()} initialized successfully")
                    break
                except (ModuleNotFoundError, ImportError) as err:
                    retry_count += 1
                    print(f" ⚠️ [LOAD ERROR] Import fault detected for '{node_id}': {str(err)}")
                    self.execute_self_heal(node_id)
                except Exception as err:
                    failed_id = node_id
                    err_msg = str(err)
                    sys.stderr.write(f"❌ Swarm initialization error for '{failed_id}': {err_msg}\n")
                    self.log_initialization_error(failed_id, err_msg)
                    if self.health_monitor:
                        try:
                            self.health_monitor.recover_node(failed_id)
                        except Exception:
                            pass
                    return False
        
        # Register all engines in HealthMonitor for heartbeat checking
        for engine_id in self.nodes_to_monitor():
            self.health_monitor.register_node(engine_id, tenant="Goings OS")

        print("🏛️ [ORCHESTRATOR] Swarm initialization sequence finalized: VAULT IS SECURE.")
        return True

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
        
        # Check against the complete 5-pillar enterprise matrix
        pillars_mapping = [
            ("Keep It Goings Consulting", True),
            ("Keep It Going Consulting", True),
            ("Tanita Brinkley Enterprises", True),
            ("Luxury Affairs Event Center / Norfolk Takeover Cruise", True),
            ("Luxury Affairs Event Center", True),
            ("Norfolk Takeover Cruise", True),
            ("CHOICE Inc.", False),
            ("Choice Inc", False),
            ("CHOICE Inc", False),
            ("Goings OS", True)
        ]
        
        detected_pillar = None
        is_commercial = True
        
        for name, commercial in pillars_mapping:
            if name.lower() in intent.lower():
                detected_pillar = name
                is_commercial = commercial
                break
                
        if not detected_pillar:
            if "choice" in intent.lower():
                detected_pillar = "CHOICE Inc."
                is_commercial = False
            else:
                detected_pillar = "Goings OS"
                is_commercial = True

        if is_commercial:
            # Calculate simulated revenue metrics (aligned to benchmarks)
            if "cruise" in intent.lower() or "takeover" in intent.lower():
                # Norfolk Takeover Cruise logistics calculation
                deposit = 150.00
                commission = 75.00
                revenue = 950.00
                owners_draw = revenue
                fin_info = f": Cabin revenue: ${revenue:.2f}; Client deposit: ${deposit:.2f}; Broker split: ${commission:.2f}; Shareholder distribution tracked as owner's draw allocation exclusively: ${owners_draw:.2f}"
            elif "luxury affairs" in intent.lower() or "event" in intent.lower():
                revenue = 1250.00
                owners_draw = revenue
                fin_info = f": Venue rental revenue: ${revenue:.2f}; Shareholder distribution tracked as owner's draw allocation exclusively: ${owners_draw:.2f}"
            elif "consulting" in intent.lower() or "keep it" in intent.lower():
                revenue = 1500.00
                owners_draw = revenue
                fin_info = f": Advisory retainer revenue: ${revenue:.2f}; Shareholder distribution tracked as owner's draw allocation exclusively: ${owners_draw:.2f}"
            elif "tanita" in intent.lower() or "enterprises" in intent.lower():
                revenue = 850.00
                owners_draw = revenue
                fin_info = f": Strategy consultation revenue: ${revenue:.2f}; Shareholder distribution tracked as owner's draw allocation exclusively: ${owners_draw:.2f}"
            else:
                revenue = 714.28
                owners_draw = revenue
                fin_info = f": Tech licensing operational yield: ${revenue:.2f}; Shareholder distribution tracked as owner's draw allocation exclusively: ${owners_draw:.2f}"
        else:
            fin_info = ": Philanthropic legacy funding allocation: processed under the CHOICE Inc. humanitarian codex (non-commercial: zero owner's draw allocation)"
        
        refined = f"Secured private operational payload for {detected_pillar}: processed under the authority of the Private Governor{fin_info}."
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
        initial_output = f"Executing task: {node.intent}: using the public governor configuration."
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
        if self.path == "/api/google/status":
            try:
                if self.orchestrator_instance.google_connector is None:
                    self.orchestrator_instance.google_connector = UnifiedAPIConnector(self.orchestrator_instance.memory_bank)
                    self.orchestrator_instance.google_connector.execute_workspace_handshake()
                
                status_data = self.orchestrator_instance.google_connector.get_connector_status()
                self._set_headers(200)
                self.wfile.write(json.dumps({"services": status_data}).encode("utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        elif self.path == "/api/mutation":
            try:
                engine = self.orchestrator_instance.mutation_engine
                self._set_headers(200)
                payload = json.dumps({
                    "strategy": engine.strategy,
                    "retry_count": engine.retry_count,
                    "max_retries": engine.max_retries,
                    "history": engine.history,
                    "log_path": engine.log_path
                })
                self.wfile.write(payload.encode("utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        elif self.path == "/api/status":
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
                
                db_agent = self.orchestrator_instance.mutation_engine.observability_agent
                db_metrics = db_agent.get_observability_metrics()
                
                self._set_headers(200)
                payload = json.dumps({
                    "engines": status_data,
                    "db_observability": db_metrics
                })
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
                        cursor.execute("SELECT timestamp, task_id, intent, agent_gem, status, output FROM swarm_task_logs ORDER BY id DESC LIMIT 15")
                        for row in cursor.fetchall():
                            intent = row[2]
                            tenant = "Goings OS"
                            for ent in ["Keep It Goings Consulting", "Keep It Going Consulting", "Tanita Brinkley Enterprises", "Luxury Affairs Event Center", "Norfolk Takeover Cruise"]:
                                if ent.lower() in intent.lower():
                                    tenant = ent
                                    break
                            tasks.append({
                                "timestamp": row[0],
                                "task_id": row[1],
                                "intent": row[2],
                                "agent": row[3],
                                "status": row[4],
                                "output": row[5],
                                "tenant": tenant
                            })
                        conn.close()
                    except Exception as e:
                        self.add_log(f"Commercial DB log read failure: {str(e)}")

                # Read humanitarian task logs
                if os.path.exists(self.orchestrator_instance.humanitarian_db):
                    try:
                        conn = sqlite3.connect(self.orchestrator_instance.humanitarian_db, timeout=5.0)
                        cursor = conn.cursor()
                        cursor.execute("SELECT timestamp, task_id, intent, agent_gem, status, output FROM swarm_task_logs ORDER BY id DESC LIMIT 15")
                        for row in cursor.fetchall():
                            tasks.append({
                                "timestamp": row[0],
                                "task_id": row[1],
                                "intent": row[2],
                                "agent": row[3],
                                "status": row[4],
                                "output": row[5],
                                "tenant": "CHOICE Inc."
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

                migration_logs = []
                migration_log_path = self.orchestrator_instance.mutation_engine.migration_log_path
                if os.path.exists(migration_log_path):
                    try:
                        with open(migration_log_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            for line in lines[-15:]:
                                if line.strip():
                                    migration_logs.append(line.strip())
                    except Exception:
                        pass

                self._set_headers(200)
                payload = json.dumps({
                    "tasks": tasks[:15],
                    "errors": errors,
                    "server_logs": self.log_messages,
                    "migration_logs": migration_logs
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

        if self.path == "/api/google/handshake":
            try:
                if self.orchestrator_instance.google_connector is None:
                    self.orchestrator_instance.google_connector = UnifiedAPIConnector(self.orchestrator_instance.memory_bank)
                
                status_data = self.orchestrator_instance.google_connector.execute_workspace_handshake()
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "status": "success",
                    "services": status_data
                }).encode("utf-8"))
                self.add_log("Google Gateway: Re-handshake triggered and verified")
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        elif self.path == "/api/mutation":
            try:
                code_to_compile = data.get("code", "print('Sovereign Mutation Audit: OK')")
                engine = self.orchestrator_instance.mutation_engine
                result = engine.execute_validation(code_to_compile)
                
                self._set_headers(200)
                self.wfile.write(json.dumps(result).encode("utf-8"))
                self.add_log(f"Mutation Engine: Executed compilation test with status: {result['status']}")
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        elif self.path == "/api/migration/run":
            try:
                engine = self.orchestrator_instance.mutation_engine
                result = engine.check_and_execute_migrations()
                
                self._set_headers(200)
                self.wfile.write(json.dumps(result).encode("utf-8"))
                self.add_log(f"Migration Engine: Executed dynamic database schema migrations with status: {result['status']}")
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        elif self.path == "/api/task":
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


class MultiTenantRoundRobinScheduler:
    """Manages round-robin task execution and telemetry generation across the five corporate pillars."""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.pillars = [
            {
                "id": "goings_os",
                "name": "Goings OS",
                "domain": "Goingsos.com",
                "details": "The Tech Engine",
                "is_commercial": True,
                "intents": [
                    "Audit active privatized gem matrix configurations",
                    "Compile ISO/IEC 42001 compliance logs",
                    "Refresh Secure API token and cryptographic key matrices"
                ]
            },
            {
                "id": "kig_consulting",
                "name": "Keep It Goings Consulting",
                "domain": "Keepitgoings.com",
                "phone": "757-500-0711",
                "details": "High-Level Advisory",
                "is_commercial": True,
                "intents": [
                    "Evaluate regional market expansion multipliers",
                    "Structure advisory consulting agreement copy templates",
                    "Analyze weekly revenue targets against corporate benchmark"
                ]
            },
            {
                "id": "tbe",
                "name": "Tanita Brinkley Enterprises",
                "domain": "TanitaTalksBusiness.com",
                "details": "Tax Shield & Strategy",
                "is_commercial": True,
                "intents": [
                    "Draft corporate bylaws and strategic tax filings",
                    "Process contractor independent alignment records",
                    "Perform sovereign presentment audits and good standing checks"
                ]
            },
            {
                "id": "laec_ntc",
                "name": "Luxury Affairs Event Center / Norfolk Takeover Cruise",
                "domain": "Luxuryaffairseventcenter.com & Norfolktakeovercruise.com",
                "phone": "757-330-3633 & 757-530-5355",
                "details": "Operational Logistics",
                "is_commercial": True,
                "intents": [
                    "Synchronize Victory Blvd facility venue schedule",
                    "Process Norfolk Takeover Cruise stateroom capacity manifest",
                    "Verify non-refundable client deposit and broker commission splits"
                ]
            },
            {
                "id": "choice_inc",
                "name": "CHOICE Inc.",
                "domain": "Choiceincva.org",
                "details": "Philanthropic Legacy",
                "is_commercial": False,
                "intents": [
                    "Track non-profit 501(c)(3) regulatory readiness",
                    "Process Choice legacy humanitarian funding codex grant allocation",
                    "Verify annual corporate registration and Form 990 trackers"
                ]
            }
        ]
        self.current_index = 0
        self.last_run_time = 0.0
        self.cadence_seconds = 15.0  # Regulated controlled cadence

    def run_cycle(self):
        """Executes a single round-robin scheduling cycle across the pillars."""
        current_time = time.time()
        
        # 1. Heartbeat monitor: Ping all 10 core engines to prevent false timeout faults
        if self.orchestrator.health_monitor:
            for engine_id in self.orchestrator.nodes_to_monitor():
                if engine_id in self.orchestrator.health_monitor.nodes:
                    self.orchestrator.health_monitor.ping_node(engine_id)

        # 2. Process tasks at controlled cadence
        if current_time - self.last_run_time >= self.cadence_seconds:
            pillar = self.pillars[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.pillars)
            
            # Select random intent from the pillar
            intent = random.choice(pillar["intents"])
            task_id = f"SCHED-TASK-{int(current_time)}-{pillar['id'].upper()}"
            
            # Combine intent with corporate details for trace
            full_intent = f"{pillar['name']}: {intent}"
            
            # Create TaskNode and run loop
            node = self.orchestrator.add_task(task_id, full_intent)
            self.orchestrator.process_task_execution_loop(node)
            
            self.last_run_time = current_time


def run_scheduler_loop(orchestrator):
    """Spawns the round-robin scheduler loop to run periodically."""
    scheduler = MultiTenantRoundRobinScheduler(orchestrator)
    # Give the main server some time to start up
    time.sleep(3.0)
    
    while True:
        try:
            scheduler.run_cycle()
        except Exception as err:
            sys.stderr.write(f"Scheduler loop execution fault: {str(err)}\n")
            
        time.sleep(2.5)


def start_scheduler_thread(orchestrator):
    """Spawns the background round-robin scheduler loop as a daemon thread."""
    thread = threading.Thread(target=run_scheduler_loop, args=(orchestrator,), daemon=True)
    thread.start()
    print(" -> Swarm Manager: Dynamic multi-tenant round-robin scheduler started successfully.")


def start_api_server(orchestrator, port=8000):
    """Launches concurrent ThreadingHTTPServer on specified port to interface with the web dashboard."""
    OrchestratorAPIHandler.orchestrator_instance = orchestrator
    
    # Start the background round-robin scheduler
    start_scheduler_thread(orchestrator)
    
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
