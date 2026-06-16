# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: NODE 13 ASYNCHRONOUS MIDNIGHT SWARM ORCHESTRATOR
# COMPLIANCE: ZERO EM-DASHES; WAL JOURNALING READY; AUTOMATED TASK PACING
# ==============================================================================

import asyncio
import datetime
import logging
import os
import sys
import time

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Importing the refactored enterprise chassis engines natively
from garnet_scout import GarnetScoutEngine
from tbe_doc_generator import TBERetainerGenerator


class GoingsOSScheduler:
    """Handles automatic execution runs for multi-pillar data harvesting pipelines."""

    def __init__(self):
        self.root_dir = os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.abspath(__file__)))
        self.log_path = os.path.join(self.root_dir, "system_faults.log")
        
        logging.basicConfig(
            filename=self.log_path,
            level=logging.ERROR,
            format="%(asctime)s UTC // SCHEDULER_LOG_EVENT // %(message)s"
        )

    def calculate_seconds_until_midnight(self) -> float:
        """Calculates precise timing intervals required to hit the midnight execution wall."""
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        midnight = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
        return (midnight - now).total_seconds()

    async def execute_midnight_swarm_sequence(self):
        """Orchestration Core: Triggers continuous lead ingestion and document builds."""
        print(f"\n🚀 [SCHEDULER] [{time.strftime('%H:%M:%S')}] Launching automated multi-agent execution sweep...")
        
        try:
            # Task Phase 1: Activate the Garnet Scout Ingestion Engine
            scout_engine = GarnetScoutEngine()
            
            # Simulated incoming enterprise stream payload matching live webhook connections
            live_webhook_payload = [
                {
                    "company": "Sovereign Logistics Holdings",
                    "email": "ops@sovereignlogistics.com",
                    "phone": "757-555-0911",
                    "market_gap": "Un-insulated cloud routing points detected",
                    "ein": "93-7771234"
                }
            ]
            
            scouted_records = scout_engine.ingest_live_stream_payload(live_webhook_payload)
            print(f" -> Phase 1 Complete: Committed {scouted_records} new unique targets to WAL repository.")
            
            # Task Phase 2: Instantly trigger the TBE Compliance Document Factory
            document_factory = TBERetainerGenerator()
            document_factory.process_all_vault_uncontracted_leads()
            print(" -> Phase 2 Complete: Clean compliance legal contracts compiled successfully.")
            print("✅ [SCHEDULER] Execution loop completed safely: returning to idling mode.")
            
        except Exception as system_fault:
            logging.error(f"Automated background scheduling loop encountered a processing failure: {str(system_fault)}")
            print("❌ CRITICAL: Background swarm experienced an error; fault isolated to log folder.")

    async def run_scheduler_daemon_loop(self, test_mode: bool = False):
        """Main non-blocking execution gate loop running background automation metrics."""
        print("==========================================================")
        print(" INITIALIZING GOINGS OS AUTOMATED SCHEDULING SYSTEM      ")
        print("==========================================================")
        print(f" -> Target Directory Baseline: {self.root_dir}")
        print(" -> System State: ONLINE // WATCHING TIMING GATES ")
        
        if test_mode:
            print("⚠️ [TEST MODE] Bypassing time-delay gates to run instant structural validation...")
            await self.execute_midnight_swarm_sequence()
            return

        while True:
            seconds_to_wait = self.calculate_seconds_until_midnight()
            print(f"💤 Idling safely: system sleeping for {seconds_to_wait:.2f} seconds until midnight wall...")
            
            # Non-blocking pause loop allows other local services to execute
            await asyncio.sleep(seconds_to_wait)
            await self.execute_midnight_swarm_sequence()
            
            # Brief pause to step over clock edge before recycling loop calculations
            await asyncio.sleep(5)


if __name__ == "__main__":
    scheduler = GoingsOSScheduler()
    
    # Run loop with instant validation enabled to immediately verify alignment
    asyncio.run(scheduler.run_scheduler_daemon_loop(test_mode=True))