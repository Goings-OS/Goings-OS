# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: AUTONOMOUS AGENT EVENT LOOP (core_nodes/autonomous_loop.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; WAL CONCURRENCY; ERROR RESILIENCE
# ==============================================================================

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional

ROOT_DIR = os.environ.get("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Load environment from root .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT_DIR, ".env"), override=True)
except ImportError:
    pass

from core_nodes.node_20_agent_bus.agent_bus import InterAgentEventBus, STANDARD_AGENT_CARDS
from core_nodes.node_18_lexis_secretary.lexis_secretary import LexisSecretaryEngine
from core_nodes.node_17_auto_updater.auto_updater import AutonomousUpdateEngine
from core_nodes.node_19_virtual_payments.virtual_payments import VirtualPaymentEngine
from core_nodes.node_21_governance_kms.governance_kms import EmergencyKillSwitch, OfacSanctionsScreening


class AutonomousAgentLoop:
    """Master Continuous Orchestration Loop for Goings-OS Sub-Agents.
    Orchestrates:
      1. Lexis-Secretary: Scans corporate registries, state deadlines, FinCEN BOIR.
      2. Titan-Infra: Polls cloud release feeds, PyPI dependencies, and git health.
      3. Inter-Agent Bus: Routes intents with @mentions and Aegis-Risk consensus.
      4. Governance KMS: Verifies zero emergency lock status.
    """

    def __init__(self, cycle_interval_seconds: int = 3600):
        self.interval = cycle_interval_seconds
        self.bus = InterAgentEventBus()
        self.lexis = LexisSecretaryEngine()
        self.updater = AutonomousUpdateEngine()
        self.vpay = VirtualPaymentEngine()
        self.kill_switch = EmergencyKillSwitch()
        self.running = False

    def run_single_cycle(self) -> Dict[str, Any]:
        """Executes a single end-to-end autonomous cycle across all core nodes."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        cycle_id = f"cycle_{int(time.time())}"
        logging.info(f"Initiating autonomous agent cycle: {cycle_id} at {timestamp}")

        # 1. Emergency Governance Check
        is_locked, lock_reason = self.kill_switch.check_system_lock_state()
        if is_locked:
            logging.warning(f"Autonomous cycle halted: System is in EMERGENCY_LOCKED state ({lock_reason}).")
            return {
                "cycle_id": cycle_id,
                "status": "HALTED_EMERGENCY_LOCK",
                "reason": lock_reason,
                "timestamp": timestamp
            }

        cycle_results: Dict[str, Any] = {
            "cycle_id": cycle_id,
            "timestamp": timestamp,
            "status": "COMPLETED",
            "nodes_executed": []
        }

        # 2. Lexis-Secretary Compliance Scan
        try:
            lexis_summary = self.lexis.run_daily_compliance_cycle()
            cycle_results["lexis_secretary"] = {
                "status": lexis_summary.get("status"),
                "scanned_entities": lexis_summary.get("total_entities_scanned"),
                "pending_filings": lexis_summary.get("pending_filings_count")
            }
            cycle_results["nodes_executed"].append("node_18_lexis_secretary")
            logging.info(f"Lexis-Secretary cycle complete. Entities: {lexis_summary.get('total_entities_scanned')}")
        except Exception as lexis_err:
            logging.error(f"Lexis-Secretary cycle error: {str(lexis_err)}")
            cycle_results["lexis_secretary"] = {"status": "ERROR", "error": str(lexis_err)}

        # 3. Titan-Infra Dependency & Cloud Health Poll (Dry-Run / Non-Destructive)
        try:
            updater_summary = self.updater.run_dry_run()
            cycle_results["titan_infra"] = {
                "status": updater_summary.get("status"),
                "branch": updater_summary.get("branch"),
                "patches_count": updater_summary.get("patches_count", 0)
            }
            cycle_results["nodes_executed"].append("node_17_auto_updater")
            logging.info(f"Titan-Infra health poll complete. Patches identified: {updater_summary.get('patches_count')}")
        except Exception as infra_err:
            logging.error(f"Titan-Infra cycle error: {str(infra_err)}")
            cycle_results["titan_infra"] = {"status": "ERROR", "error": str(infra_err)}

        # 4. Inter-Agent Event Bus Heartbeat Broadcast
        try:
            bus_evt = self.bus.publish_intent(
                sender_agent="titan-infra",
                action_name="AUTONOMOUS_CYCLE_HEARTBEAT",
                payload={
                    "cycle_id": cycle_id,
                    "active_nodes": cycle_results["nodes_executed"],
                    "timestamp": timestamp
                },
                impact_level="LOW",
                mention_text="@aegis-risk @lexis-secretary @virtual-payments"
            )
            cycle_results["agent_bus_heartbeat"] = {
                "event_id": bus_evt.get("event_id"),
                "status": bus_evt.get("status")
            }
            cycle_results["nodes_executed"].append("node_20_agent_bus")
            logging.info(f"Agent Bus heartbeat published: {bus_evt.get('event_id')}")
        except Exception as bus_err:
            logging.error(f"Agent Bus heartbeat error: {str(bus_err)}")
            cycle_results["agent_bus_heartbeat"] = {"status": "ERROR", "error": str(bus_err)}

        return cycle_results

    def start_loop(self, max_iterations: Optional[int] = None) -> None:
        """Starts continuous daemon loop executing cycles at scheduled intervals."""
        self.running = True
        iterations = 0
        logging.info(f"Starting Autonomous Agent Event Loop (Interval: {self.interval}s)")

        while self.running:
            try:
                cycle_summary = self.run_single_cycle()
                logging.info(f"Cycle {cycle_summary.get('cycle_id')} summary: {json.dumps(cycle_summary)}")
            except Exception as loop_err:
                logging.critical(f"Autonomous event loop iteration fault: {str(loop_err)}")

            iterations += 1
            if max_iterations and iterations >= max_iterations:
                logging.info(f"Max iterations ({max_iterations}) reached. Exiting event loop.")
                break

            time.sleep(self.interval)

    def stop_loop(self) -> None:
        """Gracefully halts the continuous event loop."""
        self.running = False
        logging.info("Autonomous Agent Event Loop signaled to halt.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s UTC // AUTONOMOUS_AGENT_LOOP // %(levelname)s // %(message)s"
    )
    print("==============================================================")
    print(" GOINGS OS v4.2 // AUTONOMOUS AGENT EVENT LOOP INITIATED      ")
    print(" COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; WAL MODE    ")
    print("==============================================================")

    loop_engine = AutonomousAgentLoop(cycle_interval_seconds=3600)
    # Execute initial startup cycle immediately
    initial_cycle = loop_engine.run_single_cycle()
    print("\nInitial Autonomous Cycle Execution Results:")
    print(json.dumps(initial_cycle, indent=2))
    print("\nAutonomous Agent Event Loop online and listening.")
