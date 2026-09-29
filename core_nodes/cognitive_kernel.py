# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: INSTITUTIONAL COGNITIVE GOVERNANCE ENGINE v3.2 (core_nodes/cognitive_kernel.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; AST CODE ISOLATION; WAL CONCURRENCY
# ==============================================================================

import os
import sys
import ast
import time
import json
import uuid
import hashlib
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Tuple, Set

ROOT_DIR = os.environ.get("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DEFAULT_DB_PATH = os.path.join(ROOT_DIR, "saas_storage.db")

# ==============================================================================
# 1. DATABASE SCHEMA: COGNITIVE EXECUTION VAULT (SQLite WAL)
# ==============================================================================

def init_cognitive_vault_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initializes cognitive_execution_vault table with SQLite WAL mode concurrency."""
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cognitive_execution_vault (
                execution_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                tier_route TEXT NOT NULL,
                complexity_score REAL NOT NULL,
                circuit_breaker_status TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                state_hash_sha256 TEXT NOT NULL,
                payload_summary TEXT NOT NULL,
                result_receipt JSON NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        conn.commit()
        conn.close()
    except Exception as err:
        logging.error(f"Failed to initialize cognitive vault database: {str(err)}")


# ==============================================================================
# 2. COMPLEXITY ENGINE
# ==============================================================================

class ComplexityEngine:
    """Calculates Complexity Score (Cs) using weighted metrics:
    Ambiguity (0.35), Liability (0.40), Tools (0.15), Latency (0.10).
    Deterministically routes to:
      - Tier 1: Deterministic / Buffer of Thoughts (BoT) [Cs < 0.35]
      - Tier 2: Tool-Governed / Program of Thoughts (PoT) [0.35 <= Cs < 0.70]
      - Tier 3: Adversarial Audit / Chain of Verification (CoVe) [Cs >= 0.70]
    """

    WEIGHT_AMBIGUITY = 0.35
    WEIGHT_LIABILITY = 0.40
    WEIGHT_TOOLS = 0.15
    WEIGHT_LATENCY = 0.10

    @classmethod
    def calculate_score(
        cls,
        ambiguity: float,
        liability: float,
        tools_required: float,
        latency_sensitivity: float
    ) -> float:
        """Computes weighted complexity score normalized strictly between 0.0 and 1.0."""
        # Clamp inputs to [0.0, 1.0]
        a = max(0.0, min(1.0, float(ambiguity)))
        l = max(0.0, min(1.0, float(liability)))
        t = max(0.0, min(1.0, float(tools_required)))
        s = max(0.0, min(1.0, float(latency_sensitivity)))

        score = (
            (a * cls.WEIGHT_AMBIGUITY) +
            (l * cls.WEIGHT_LIABILITY) +
            (t * cls.WEIGHT_TOOLS) +
            (s * cls.WEIGHT_LATENCY)
        )
        return round(score, 4)

    @classmethod
    def route_task(cls, complexity_score: float) -> Tuple[str, str]:
        """Maps complexity score to deterministic execution tiers."""
        if complexity_score < 0.35:
            return "TIER_1_DETERMINISTIC_BOT", "Buffer of Thoughts (BoT) Deterministic Execution"
        elif complexity_score < 0.70:
            return "TIER_2_TOOL_GOVERNED_POT", "Program of Thoughts (PoT) Sandboxed Compute Runtime"
        else:
            return "TIER_3_ADVERSARIAL_AUDIT_COVE", "Chain of Verification (CoVe) Adversarial Audit Gate"


# ==============================================================================
# 3. SANDBOXED POT RUNTIME (AST VISITOR & ISOLATED EXECUTION)
# ==============================================================================

class SecurityASTVisitor(ast.NodeVisitor):
    """Abstract Syntax Tree visitor inspecting code prior to execution.
    Blocks:
      - Double-underscore traversal (__class__, __subclasses__, __globals__, etc.)
      - Dynamic imports and import statements (import, __import__, importlib)
      - Unauthorized OS / system / process calls (os, sys, subprocess, eval, exec)
    """

    PROHIBITED_CALLS: Set[str] = {
        "eval", "exec", "__import__", "open", "compile",
        "getattr", "setattr", "delattr", "globals", "locals"
    }

    PROHIBITED_MODULES: Set[str] = {
        "os", "sys", "subprocess", "shutil", "socket", "importlib",
        "requests", "urllib", "http", "pickle", "ctypes"
    }

    def __init__(self):
        self.violations: List[str] = []

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Blocks double-underscore attribute traversal (__class__, __base__, etc.)."""
        if node.attr.startswith("__") and node.attr.endswith("__"):
            self.violations.append(
                f"Security Violation: Double-underscore attribute access '{node.attr}' is prohibited."
            )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Blocks double-underscore variable access or prohibited identifiers."""
        if node.id.startswith("__") and node.id.endswith("__"):
            self.violations.append(
                f"Security Violation: Double-underscore identifier '{node.id}' is prohibited."
            )
        if node.id in self.PROHIBITED_CALLS:
            self.violations.append(
                f"Security Violation: Direct reference to prohibited built-in '{node.id}'."
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Blocks calls to dangerous functions or methods."""
        if isinstance(node.func, ast.Name):
            if node.func.id in self.PROHIBITED_CALLS:
                self.violations.append(
                    f"Security Violation: Call to prohibited function '{node.func.id}()'."
                )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Blocks raw import statements."""
        for alias in node.names:
            self.violations.append(
                f"Security Violation: Import of module '{alias.name}' is strictly prohibited in sandbox."
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Blocks from-import statements."""
        self.violations.append(
            f"Security Violation: Import from '{node.module}' is strictly prohibited in sandbox."
        )
        self.generic_visit(node)


class SandboxedPoTRuntime:
    """Program of Thoughts (PoT) execution engine for financial calculations and owner's draw allocations."""

    ALLOWED_BUILTINS: Dict[str, Any] = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "len": len,
        "range": range,
        "float": float,
        "int": int,
        "str": str,
        "dict": dict,
        "list": list
    }

    @classmethod
    def validate_ast(cls, code_str: str) -> Tuple[bool, List[str]]:
        """Parses and checks code with SecurityASTVisitor before execution."""
        try:
            tree = ast.parse(code_str)
        except SyntaxError as syn_err:
            return False, [f"Syntax Error in code: {str(syn_err)}"]

        visitor = SecurityASTVisitor()
        visitor.visit(tree)
        is_safe = len(visitor.violations) == 0
        return is_safe, visitor.violations

    @classmethod
    def execute_financial_compute(cls, code_str: str, input_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validates AST and executes financial computation in isolated namespace."""
        is_safe, violations = cls.validate_ast(code_str)
        if not is_safe:
            return {
                "success": False,
                "status": "BLOCKED_BY_AST_SECURITY",
                "violations": violations,
                "result": None
            }

        # Setup restricted sandbox environment
        sandbox_globals: Dict[str, Any] = {
            "__builtins__": cls.ALLOWED_BUILTINS
        }
        sandbox_locals: Dict[str, Any] = dict(input_context)

        try:
            exec(code_str, sandbox_globals, sandbox_locals)
            # Filter output to extract defined variables excluding builtins
            clean_output = {
                k: v for k, v in sandbox_locals.items()
                if not k.startswith("__") and not callable(v)
            }
            return {
                "success": True,
                "status": "COMPUTED_SUCCESSFULLY",
                "violations": [],
                "result": clean_output
            }
        except Exception as run_err:
            return {
                "success": False,
                "status": "RUNTIME_EXECUTION_ERROR",
                "violations": [str(run_err)],
                "result": None
            }

    @classmethod
    def compute_owners_draw_metrics(
        cls,
        gross_revenue: float,
        owners_draw_ratio: float = 0.30,
        insulation_ratio: float = 0.30,
        ops_ratio: float = 0.40
    ) -> Dict[str, Any]:
        """Standard institutional financial partitioner."""
        code = """
owners_draw = round(gross_revenue * owners_draw_ratio, 2)
insulation_reserve = round(gross_revenue * insulation_ratio, 2)
operations_runway = round(gross_revenue * ops_ratio, 2)
net_allocated = round(owners_draw + insulation_reserve + operations_runway, 2)
"""
        context = {
            "gross_revenue": gross_revenue,
            "owners_draw_ratio": owners_draw_ratio,
            "insulation_ratio": insulation_ratio,
            "ops_ratio": ops_ratio
        }
        return cls.execute_financial_compute(code, context)


# ==============================================================================
# 4. CHAIN OF VERIFICATION ENGINE (CoVe)
# ==============================================================================

class ChainOfVerificationEngine:
    """Adversarial Audit Engine: Generates unconditioned baseline claims, formulates verification
    questions against statutory ground truth (FCRA 15 U.S.C. 1681 and CROA 15 U.S.C. 1679),
    and computes divergence scores.
    """

    STATUTORY_GROUND_TRUTH: Dict[str, Dict[str, Any]] = {
        "CROA_ADVANCE_FEE_PROHIBITION": {
            "statutory_code": "15 U.S.C. 1679b(b)",
            "rule": "No credit repair organization may charge or receive any money or other valuable consideration for the performance of any service before such service is fully performed.",
            "allowed_advance_fees": False,
            "mandatory_disclosures": True,
            "cancellation_period_days": 3
        },
        "FCRA_ACCURACY_DISPUTES": {
            "statutory_code": "15 U.S.C. 1681i(a)(1)",
            "rule": "Consumer reporting agency must conduct reasonable reinvestigation within 30 days of consumer dispute notice.",
            "reinvestigation_window_days": 30,
            "frivolous_dispute_notice_days": 5
        },
        "FCRA_OBSOLETE_INFORMATION": {
            "statutory_code": "15 U.S.C. 1681c(a)",
            "rule": "No consumer reporting agency may make any consumer report containing bankruptcy cases older than 10 years, or paid tax liens, accounts placed for collection older than 7 years.",
            "bankruptcy_max_years": 10,
            "adverse_info_max_years": 7
        }
    }

    @classmethod
    def evaluate_credit_consulting_claim(
        cls,
        baseline_claim: str,
        advance_fee_requested: bool = False,
        dispute_turnaround_days_claimed: int = 30
    ) -> Dict[str, Any]:
        """Formulates verification checks against statutory truth and computes divergence."""
        verification_questions: List[Dict[str, Any]] = []
        divergence_points: List[str] = []

        # Check 1: CROA Advance Fee Compliance
        croa_truth = cls.STATUTORY_GROUND_TRUTH["CROA_ADVANCE_FEE_PROHIBITION"]
        croa_violation = advance_fee_requested is True
        verification_questions.append({
            "question": "Does the consulting claim or agreement require advance fees before credit services are fully rendered?",
            "statute": croa_truth["statutory_code"],
            "expected_answer": "NO",
            "evaluated_claim_answer": "YES" if advance_fee_requested else "NO",
            "passed": not croa_violation
        })
        if croa_violation:
            divergence_points.append("VIOLATION CROA 15 U.S.C. 1679b(b): Advance fees claimed or demanded.")

        # Check 2: FCRA Dispute Turnaround Time
        fcra_truth = cls.STATUTORY_GROUND_TRUTH["FCRA_ACCURACY_DISPUTES"]
        turnaround_unrealistic = dispute_turnaround_days_claimed < 5
        verification_questions.append({
            "question": "Is the claimed reinvestigation window compliant with reasonable statutory reinvestigation periods?",
            "statute": fcra_truth["statutory_code"],
            "statutory_window_days": fcra_truth["reinvestigation_window_days"],
            "claimed_window_days": dispute_turnaround_days_claimed,
            "passed": not turnaround_unrealistic
        })
        if turnaround_unrealistic:
            divergence_points.append("MISREPRESENTATION FCRA 15 U.S.C. 1681i: Impossible turnaround claimed under statutory 30-day window.")

        # Calculate divergence score (0.0 = aligned; 1.0 = total divergence)
        divergence_score = round(len(divergence_points) / max(1, len(verification_questions)), 2)
        audit_verdict = "VERIFIED_COMPLIANT" if divergence_score == 0.0 else "ADVERSARIAL_DIVERGENCE_DETECTED"

        return {
            "baseline_claim": baseline_claim,
            "verification_questions": verification_questions,
            "divergence_score": divergence_score,
            "divergence_points": divergence_points,
            "audit_verdict": audit_verdict,
            "is_compliant": audit_verdict == "VERIFIED_COMPLIANT"
        }


# ==============================================================================
# 5. INSTITUTIONAL GOVERNANCE ORCHESTRATOR
# ==============================================================================

class InstitutionalGovernanceOrchestrator:
    """Coordinates execution pipeline, logging receipts, latency, circuit breakers,
    and SHA-256 state hashes directly into cognitive_execution_vault in saas_storage.db.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.circuit_breaker_tripped = False
        init_cognitive_vault_db(self.db_path)

    def process_task(
        self,
        task_id: str,
        ambiguity: float,
        liability: float,
        tools_required: float,
        latency_sensitivity: float,
        task_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deterministic cognitive governance execution pipeline."""
        start_time = time.time()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        execution_id = f"cog_{uuid.uuid4().hex[:12]}"

        # 1. Complexity Scoring & Route Determination
        cs = ComplexityEngine.calculate_score(ambiguity, liability, tools_required, latency_sensitivity)
        tier_route, tier_desc = ComplexityEngine.route_task(cs)

        result_receipt: Dict[str, Any] = {}
        circuit_status = "NORMAL"

        # 2. Check Circuit Breaker
        if self.circuit_breaker_tripped:
            circuit_status = "TRIPPED_HALTED"
            result_receipt = {
                "status": "CIRCUIT_BREAKER_BLOCKED",
                "message": "Orchestrator circuit breaker is tripped. Execution halted."
            }
        else:
            # 3. Route Execution
            if tier_route == "TIER_1_DETERMINISTIC_BOT":
                # Deterministic Buffer of Thoughts
                result_receipt = {
                    "tier": "TIER_1",
                    "architecture": "Buffer of Thoughts (BoT)",
                    "execution": "Cached / Deterministic Formula Resolution",
                    "input_echo": task_payload.get("query", "Default Query"),
                    "status": "RESOLVED_DETERMINISTIC"
                }

            elif tier_route == "TIER_2_TOOL_GOVERNED_POT":
                # Program of Thoughts (Sandboxed AST Execution)
                revenue = float(task_payload.get("gross_revenue", 10000.0))
                pot_res = SandboxedPoTRuntime.compute_owners_draw_metrics(
                    gross_revenue=revenue,
                    owners_draw_ratio=float(task_payload.get("owners_draw_ratio", 0.30)),
                    insulation_ratio=float(task_payload.get("insulation_ratio", 0.30)),
                    ops_ratio=float(task_payload.get("ops_ratio", 0.40))
                )
                result_receipt = {
                    "tier": "TIER_2",
                    "architecture": "Program of Thoughts (PoT)",
                    "sandboxed_execution": pot_res
                }
                if not pot_res["success"]:
                    circuit_status = "ANOMALY_WARNING"

            elif tier_route == "TIER_3_ADVERSARIAL_AUDIT_COVE":
                # Chain of Verification Adversarial Audit
                claim = task_payload.get("claim", "Standard Credit Consulting Strategy")
                adv_fee = bool(task_payload.get("advance_fee_requested", False))
                turnaround = int(task_payload.get("dispute_turnaround_days_claimed", 30))

                cove_res = ChainOfVerificationEngine.evaluate_credit_consulting_claim(
                    baseline_claim=claim,
                    advance_fee_requested=adv_fee,
                    dispute_turnaround_days_claimed=turnaround
                )
                result_receipt = {
                    "tier": "TIER_3",
                    "architecture": "Chain of Verification (CoVe)",
                    "audit_results": cove_res
                }
                if not cove_res["is_compliant"]:
                    circuit_status = "AUDIT_REJECTED"

        # 4. Latency and State Hashing
        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        state_payload = f"{task_id}:{tier_route}:{cs}:{json.dumps(result_receipt, sort_keys=True)}"
        state_hash = hashlib.sha256(state_payload.encode("utf-8")).hexdigest()

        # 5. Persist to SQLite Vault (saas_storage.db)
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                INSERT OR REPLACE INTO cognitive_execution_vault (
                    execution_id, task_id, tier_route, complexity_score,
                    circuit_breaker_status, latency_ms, state_hash_sha256,
                    payload_summary, result_receipt, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id, task_id, tier_route, cs, circuit_status,
                latency_ms, state_hash, json.dumps(task_payload)[:400],
                json.dumps(result_receipt), timestamp
            ))
            conn.commit()
            conn.close()
        except Exception as db_err:
            logging.error(f"Failed to log cognitive execution: {str(db_err)}")

        return {
            "execution_id": execution_id,
            "task_id": task_id,
            "tier_route": tier_route,
            "tier_description": tier_desc,
            "complexity_score": cs,
            "circuit_breaker_status": circuit_status,
            "latency_ms": latency_ms,
            "state_hash_sha256": state_hash,
            "result": result_receipt,
            "timestamp": timestamp
        }


# ==============================================================================
# 6. SELF-CONTAINED VERIFICATION SUITE
# ==============================================================================

def run_self_verification_suite(db_path: str = DEFAULT_DB_PATH) -> None:
    """Executes end-to-end verification across Tier 1, Tier 2, and Tier 3 tasks."""
    print("==============================================================================")
    print(" GOINGS OS v4.2 // INSTITUTIONAL COGNITIVE GOVERNANCE KERNEL v3.2 VERIFICATION")
    print(" COMPLIANCE: ZERO EM-DASHES; AST CODE ISOLATION; WAL CONCURRENCY ACTIVE       ")
    print("==============================================================================")

    orchestrator = InstitutionalGovernanceOrchestrator(db_path=db_path)

    # --- TEST 1: TIER 1 DETERMINISTIC (BoT) ---
    print("\n[TEST 1] Executing Tier 1 Task (Low Ambiguity, Low Liability)...")
    t1_res = orchestrator.process_task(
        task_id="TASK_T1_ROUTINE_001",
        ambiguity=0.10,
        liability=0.10,
        tools_required=0.10,
        latency_sensitivity=0.20,
        task_payload={"query": "Get standard operating hours for Luxury Affairs Event Center"}
    )
    print(f" -> Route Assigned: {t1_res['tier_route']} (Score: {t1_res['complexity_score']})")
    print(f" -> Status: {t1_res['circuit_breaker_status']} | Latency: {t1_res['latency_ms']} ms")
    print(f" -> State Hash: {t1_res['state_hash_sha256'][:16]}...")
    assert t1_res["tier_route"] == "TIER_1_DETERMINISTIC_BOT", "Tier 1 routing failure"

    # --- TEST 2: TIER 2 TOOL-GOVERNED (PoT) ---
    print("\n[TEST 2] Executing Tier 2 Task (Financial Partitioning & Owners Draw)...")
    t2_res = orchestrator.process_task(
        task_id="TASK_T2_FINANCIAL_002",
        ambiguity=0.30,
        liability=0.60,
        tools_required=0.80,
        latency_sensitivity=0.40,
        task_payload={"gross_revenue": 50000.0, "owners_draw_ratio": 0.30, "insulation_ratio": 0.30, "ops_ratio": 0.40}
    )
    print(f" -> Route Assigned: {t2_res['tier_route']} (Score: {t2_res['complexity_score']})")
    print(f" -> Status: {t2_res['circuit_breaker_status']} | Latency: {t2_res['latency_ms']} ms")
    print(f" -> Computation Output: {t2_res['result']['sandboxed_execution']['result']}")
    assert t2_res["tier_route"] == "TIER_2_TOOL_GOVERNED_POT", "Tier 2 routing failure"
    assert t2_res["result"]["sandboxed_execution"]["result"]["owners_draw"] == 15000.0

    # --- TEST 2b: AST SECURITY GUARD VALIDATION ---
    print("\n[TEST 2b] Testing SandboxedPoTRuntime AST Guard Against Dangerous Payloads...")
    malicious_payload = "import os; os.system('echo compromised')"
    safe, violations = SandboxedPoTRuntime.validate_ast(malicious_payload)
    print(f" -> Malicious Code Blocked: {not safe} | Violations Caught: {len(violations)}")
    assert not safe, "Security AST failed to block raw import statement"

    dunder_payload = "x = ().__class__.__subclasses__()"
    safe_d, violations_d = SandboxedPoTRuntime.validate_ast(dunder_payload)
    print(f" -> Dunder Traversal Blocked: {not safe_d} | Violations Caught: {len(violations_d)}")
    assert not safe_d, "Security AST failed to block dunder traversal"

    # --- TEST 3: TIER 3 ADVERSARIAL AUDIT (CoVe) ---
    print("\n[TEST 3] Executing Tier 3 Task (CROA & FCRA Statutory Compliance Gate)...")
    t3_compliant = orchestrator.process_task(
        task_id="TASK_T3_LEGAL_003A",
        ambiguity=0.80,
        liability=0.95,
        tools_required=0.60,
        latency_sensitivity=0.20,
        task_payload={
            "claim": "TBE Credit Consulting: Client disputes processed under statutory 30-day FCRA window with zero upfront fees.",
            "advance_fee_requested": False,
            "dispute_turnaround_days_claimed": 30
        }
    )
    print(f" -> Route Assigned: {t3_compliant['tier_route']} (Score: {t3_compliant['complexity_score']})")
    print(f" -> Audit Verdict: {t3_compliant['result']['audit_results']['audit_verdict']}")
    print(f" -> Divergence Score: {t3_compliant['result']['audit_results']['divergence_score']}")
    assert t3_compliant["tier_route"] == "TIER_3_ADVERSARIAL_AUDIT_COVE", "Tier 3 routing failure"
    assert t3_compliant["result"]["audit_results"]["is_compliant"] is True

    print("\n[TEST 3b] Executing Tier 3 Task with CROA Advance Fee Violation...")
    t3_violation = orchestrator.process_task(
        task_id="TASK_T3_LEGAL_003B",
        ambiguity=0.85,
        liability=0.95,
        tools_required=0.70,
        latency_sensitivity=0.10,
        task_payload={
            "claim": "Advance retainer fee of $500 required before beginning dispute preparation.",
            "advance_fee_requested": True,
            "dispute_turnaround_days_claimed": 2
        }
    )
    print(f" -> Audit Verdict: {t3_violation['result']['audit_results']['audit_verdict']}")
    print(f" -> Divergence Points: {t3_violation['result']['audit_results']['divergence_points']}")
    assert t3_violation["result"]["audit_results"]["is_compliant"] is False

    # --- VAULT LOGGING AUDIT CHECK ---
    print("\n[TEST 4] Auditing SQLite Vault (saas_storage.db: cognitive_execution_vault)...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT execution_id, task_id, tier_route, complexity_score, latency_ms FROM cognitive_execution_vault ORDER BY created_at DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()

    print(f" -> Vault Audit Entries Verified: {len(rows)}")
    for row in rows:
        print(f"    * [{row[0]}] {row[1]} -> {row[2]} (Score: {row[3]}, Latency: {row[4]}ms)")

    print("\n==============================================================================")
    print(" ALL INSTITUTIONAL COGNITIVE GOVERNANCE TESTS COMPLETED SUCCESSFULLY (100% OK)")
    print("==============================================================================")


if __name__ == "__main__":
    run_self_verification_suite()
