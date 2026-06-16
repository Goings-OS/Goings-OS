# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: COMPLIANCE ROUTING FIREWALL & ROUTING CONTROLLER
# COMPLIANCE: ZERO EM-DASHES; ABSOLUTE SECURE DATA SEPARATION
# ==============================================================================

import os
import sys
import re
import time

# Ensure parent directory is in sys.path when running this module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_nodes.memory_bank import PersistentMemoryBank

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class ComplianceRouter:
    """Acts as the compliance logical firewall between agent decisions and output layers."""

    # Corporate business rule constraints from Gemini.md
    REVENUE_FLOOR_WEEKLY = 5000.00
    OPERATIONAL_YIELD_DAILY = 714.28
    CRUISE_MAX_SOULS = 400
    CRUISE_MIN_DEPOSIT = 150.00
    CRUISE_BROKER_COMMISSION = 75.00

    def __init__(self, memory_bank: PersistentMemoryBank = None):
        self.memory_bank = memory_bank or PersistentMemoryBank()

    def enforce_rules(self, task_id: str, output: str, metadata: dict = None) -> tuple[bool, list[str]]:
        """Scans incoming task outputs against a hard-coded matrix of business rules."""
        violations = []

        # 1. Typographical Checks (Total and absolute prohibition of em-dashes)
        if "\u2014" in output or "--" in output:
            violations.append("Typographical Rule: Literal em-dashes are prohibited: utilize colons or semicolons exclusively.")

        # 2. Terminology Mandate Checks (Always utilize 'Private' and 'Private Governor')
        uninsulated_terms = ["public governor", "global governor", "uninsulated", "un-insulated"]
        for term in uninsulated_terms:
            if term in output.lower():
                violations.append(f"Terminology Mandate: Prohibited term '{term}' detected. Use 'Private' or 'Private Governor' formulations.")

        # 3. Shareholder Distribution Checks (Track as owner's draw allocations exclusively)
        distribution_terms = ["shareholder distribution", "shareholder distributions", "dividend", "dividends", "profit distribution"]
        has_dist_term = any(term in output.lower() for term in distribution_terms)
        if has_dist_term:
            if "owner's draw" not in output.lower():
                violations.append("Financial Rule: Shareholder distributions must be structurally logged and tracked as owner's draw allocations exclusively.")

        # 4. Norfolk Takeover Cruise Checks
        is_cruise_related = "norfolk takeover cruise" in output.lower() or "cruise" in output.lower() or (metadata and metadata.get("is_cruise_related"))
        if is_cruise_related:
            # Manifest Capacity checks
            capacity = None
            if metadata and "cruise_capacity" in metadata:
                capacity = metadata["cruise_capacity"]
            else:
                match = re.search(r"(?:capacity|souls|passengers|staterooms|manifest)\b\D*([\d,]+)", output, re.IGNORECASE)
                if match:
                    capacity = int(match.group(1).replace(",", ""))

            if capacity is not None and capacity > self.CRUISE_MAX_SOULS:
                violations.append(f"Cruise Constraint: manifest capacity {capacity} exceeds the maximum threshold of {self.CRUISE_MAX_SOULS} souls.")

            # Base Deposit checks (non-refundable)
            deposit = None
            is_refundable = None
            if metadata and "cruise_deposit" in metadata:
                deposit = metadata["cruise_deposit"]
                is_refundable = metadata.get("is_refundable", True)
            else:
                match_dep = re.search(r"deposit\b\D*([\d,]+(?:\.\d+)?)", output, re.IGNORECASE)
                if match_dep:
                    deposit = float(match_dep.group(1).replace(",", ""))
                if "non-refundable" in output.lower() or "non refundable" in output.lower():
                    is_refundable = False
                elif "refundable" in output.lower():
                    is_refundable = True

            if deposit is not None:
                if deposit < self.CRUISE_MIN_DEPOSIT:
                    violations.append(f"Cruise Constraint: base client deposit {deposit:.2f} is less than the required {self.CRUISE_MIN_DEPOSIT:.2f} threshold.")
                if is_refundable is not False and ("deposit" in output.lower() or (metadata and "cruise_deposit" in metadata)):
                    violations.append("Cruise Constraint: base client deposit must be designated as strictly non-refundable.")

            # Broker Commission split checks
            commission = None
            if metadata and "broker_commission" in metadata:
                commission = metadata["broker_commission"]
            else:
                match_comm = re.search(r"(?:commission|split)\b\D*([\d,]+(?:\.\d+)?)", output, re.IGNORECASE)
                if match_comm:
                    commission = float(match_comm.group(1).replace(",", ""))

            if commission is not None and commission != self.CRUISE_BROKER_COMMISSION:
                violations.append(f"Cruise Constraint: broker commission split {commission:.2f} must be exactly fixed at {self.CRUISE_BROKER_COMMISSION:.2f}.")

        # 5. Corporate Revenue and Yield Checks
        weekly_rev = None
        if metadata and "weekly_revenue" in metadata:
            weekly_rev = metadata["weekly_revenue"]
        else:
            match_weekly = re.search(r"(?:weekly revenue|revenue floor|per week|weekly)\b\D*([\d,]+(?:\.\d+)?)", output, re.IGNORECASE)
            if match_weekly:
                weekly_rev = float(match_weekly.group(1).replace(",", ""))
        if weekly_rev is not None and weekly_rev < self.REVENUE_FLOOR_WEEKLY:
            violations.append(f"Revenue Benchmark: Weekly revenue benchmark {weekly_rev:.2f} falls below the required {self.REVENUE_FLOOR_WEEKLY:.2f} floor.")

        daily_yield = None
        if metadata and "daily_yield" in metadata:
            daily_yield = metadata["daily_yield"]
        else:
            match_daily = re.search(r"(?:daily operational yield|daily yield|daily benchmark|daily)\b\D*([\d,]+(?:\.\d+)?)", output, re.IGNORECASE)
            if match_daily:
                daily_yield = float(match_daily.group(1).replace(",", ""))
        if daily_yield is not None and daily_yield < self.OPERATIONAL_YIELD_DAILY:
            violations.append(f"Revenue Benchmark: Daily operational yield {daily_yield:.2f} falls below the required {self.OPERATIONAL_YIELD_DAILY:.2f} benchmark.")

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def route_to_governor(self, task_id: str, output: str, violations: list[str]):
        """Fallback routing: directs output payloads failing compliance checks to the human-in-the-loop Governor."""
        print(f"\n⚠️ [COMPLIANCE ROUTER] Task {task_id} FAILED compliance check.")
        print(" -> Violations detected:")
        for violation in violations:
            print(f"    * {violation}")
        print(" -> Routing action: FALLBACK TO PRIVATE GOVERNOR ENGAGED")

    def log_routing_decision(self, task_id: str, output: str, is_compliant: bool, violations: list[str], metadata: dict = None):
        """Persists the evaluation results and routing actions directly inside the SQLite memory bank."""
        tenant = "Goings OS"
        if "choice" in task_id.lower() or "choice" in output.lower() or (metadata and metadata.get("tenant") == "Choice Inc"):
            tenant = "Choice Inc"

        context_key = f"COMPLIANCE_ROUTING_{task_id}"
        context_value = f"Status: {'APPROVED' if is_compliant else 'ROUTED_TO_GOVERNOR'}"

        log_meta = {
            "task_id": task_id,
            "is_compliant": is_compliant,
            "violations": violations,
            "routing_destination": "Output Layer" if is_compliant else "Governor",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        if metadata:
            log_meta.update({k: v for k, v in metadata.items() if k != "vector_embeddings"})

        self.memory_bank.store_context(context_key, context_value, log_meta, tenant=tenant)

    def route_task_output(self, task_id: str, output: str, metadata: dict = None) -> str:
        """Evaluates output, routes appropriately, logs decision, and returns target destination."""
        is_compliant, violations = self.enforce_rules(task_id, output, metadata)
        self.log_routing_decision(task_id, output, is_compliant, violations, metadata)

        if not is_compliant:
            self.route_to_governor(task_id, output, violations)
            return "GOVERNOR"
        else:
            print(f"\n✅ [COMPLIANCE ROUTER] Task {task_id} PASSED compliance check. Routing to output layer.")
            return "OUTPUT_LAYER"


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS DETERMINISTIC COMPLIANCE ROUTER    ")
    print("==========================================================")
    
    router = ComplianceRouter()
    
    # Run test check on a compliant payload
    compliant_payload = "Secured private operational payload: processed under the authority of the Private Governor."
    dest = router.route_task_output("DEMO-TASK-001", compliant_payload)
    print(f" -> Destination: {dest}")

    # Run test check on a payload violating the em-dash rule
    non_compliant_payload = "Processing system output \u2014 utilizing the default settings."
    dest_failed = router.route_task_output("DEMO-TASK-002", non_compliant_payload)
    print(f" -> Destination: {dest_failed}")
    print("==========================================================")
