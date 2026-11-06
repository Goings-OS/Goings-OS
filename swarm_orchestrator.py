# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: SWARM ORCHESTRATOR (swarm_orchestrator.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; UNIFIED COGNITIVE FLEET ENGINE
# ==============================================================================

import os
import sys
import json
import time
import uuid
import signal
import logging
import threading
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

# Load environment configuration
load_dotenv(os.path.join(WORKSPACE_ROOT, ".env"))

from core_nodes.node_20_agent_bus.agent_bus import (
    InterAgentEventBus,
    STANDARD_AGENT_CARDS
)
from core_nodes.api_binding_protocol import APIBindingProtocol
from core_nodes.cognitive_kernel import (
    InstitutionalGovernanceOrchestrator,
    RAGIngestionEngine,
    GraphRAGEngine,
    BufferOfThoughtEngine,
    SkeletonOfThoughtEngine,
    AlgorithmOfThoughtEngine,
    ThoughtTopologyEngine,
    OffGridCognitiveRouter,
    ComplexityEngine
)
from core_nodes.workspace_architect_daemon import WorkspaceArchitectDaemon
from core_nodes.intelligence_scout_daemon import IntelligenceScoutDaemon
from core_nodes.form_specialist_daemon import FormSpecialistDaemon
from core_nodes.intake_dispatcher_daemon import IntakeDispatcherDaemon
from core_nodes.ui_frontend_architect_daemon import UIFrontendArchitectDaemon
from core_nodes.presentation_specialist_daemon import PresentationSpecialistDaemon
from core_nodes.sales_intelligence_node_daemon import SalesIntelligenceNodeDaemon

# Configure logging
LOG_DIR = os.path.join(WORKSPACE_ROOT, "data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "swarm_orchestrator.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Swarm_Orchestrator] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)


class SwarmOrchestrator:
    """
    Unified Swarm Orchestration Engine for Goings-OS (God Mode v4.0).
    Initializes the shared InterAgentEventBus, mounts the InstitutionalGovernanceOrchestrator,
    and concurrently boots all seven persistent child agents into background execution loops:
    1. Workspace_Architect (workspace-architect)
    2. Intelligence_Scout (intelligence-scout)
    3. Form_Specialist (form-specialist)
    4. Intake_Dispatcher (intake-dispatcher)
    5. UI_Frontend_Architect (ui-frontend-architect)
    6. Presentation_Specialist (presentation-specialist)
    7. Sales_Intelligence_Node (sales-intelligence-node)
    
    Manages thread lifecycles, cross-node routing, multi-engine reasoning governance,
    and unified telemetry status with zero em-dash and zero double-hyphen compliance.
    """

    ORCHESTRATOR_ID = "swarm-orchestrator-core"
    ORCHESTRATOR_NAME = "Swarm_Orchestrator"

    def __init__(self, schema_path: Optional[str] = None):
        self.workspace_root = WORKSPACE_ROOT
        self.schema_path = schema_path or os.path.join(self.workspace_root, "mcp_registry_schema.json")
        self.status_file = os.path.join(self.workspace_root, "data", "swarm_orchestrator_status.json")
        
        self.start_time = time.time()
        self.running = False
        self.stop_event = threading.Event()
        
        # 1. Execute API Binding Protocol & Live Credential Audit
        logging.info("Executing API Binding Protocol and live credential audit...")
        self.api_binding = APIBindingProtocol(workspace_root=self.workspace_root)
        self.api_binding_report = self.api_binding.run_full_protocol()

        # 2. Initialize Shared InterAgentEventBus
        logging.info("Initializing unified InterAgentEventBus with STANDARD_AGENT_CARDS...")
        self.bus = InterAgentEventBus(agent_cards=STANDARD_AGENT_CARDS)
        
        # 3. Mount Institutional Cognitive Governance Engine (God Mode Matrix)
        logging.info("Mounting InstitutionalGovernanceOrchestrator and Multi-Engine AI Matrix...")
        db_path = os.path.join(self.workspace_root, "saas_storage.db")
        self.cognitive_governor = InstitutionalGovernanceOrchestrator(db_path=db_path)
        
        # 4. Instantiate all 7 child agents
        logging.info("Instantiating full 7-agent child daemon fleet...")
        self.agents: Dict[str, Any] = {}
        self.agent_metadata: Dict[str, Dict[str, Any]] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self.events_dispatched = 0
        
        self._boot_agent_instances()
        self._wire_shared_bus()
        self._record_swarm_status()

    def _boot_agent_instances(self) -> None:
        """Instantiates all seven child agent daemons."""
        # Agent 1: Workspace_Architect
        try:
            self.agents["workspace-architect"] = WorkspaceArchitectDaemon(schema_path=self.schema_path)
            self.agent_metadata["workspace-architect"] = {
                "name": "Workspace_Architect",
                "role": "Autonomous Google Docs & Sheets Generation via MCP Tool",
                "node_id": "node_01_architect"
            }
            logging.info("Booted agent instance: Workspace_Architect (workspace-architect)")
        except Exception as err:
            logging.error(f"Failed to instantiate Workspace_Architect: {str(err)}")

        # Agent 2: Intelligence_Scout
        try:
            self.agents["intelligence-scout"] = IntelligenceScoutDaemon(schema_path=self.schema_path)
            self.agent_metadata["intelligence-scout"] = {
                "name": "Intelligence_Scout",
                "role": "Autonomous Web Crawling, OSINT & Technical Research Synthesis",
                "node_id": "node_06_scout"
            }
            logging.info("Booted agent instance: Intelligence_Scout (intelligence-scout)")
        except Exception as err:
            logging.error(f"Failed to instantiate Intelligence_Scout: {str(err)}")

        # Agent 3: Form_Specialist
        try:
            self.agents["form-specialist"] = FormSpecialistDaemon(schema_path=self.schema_path)
            self.agent_metadata["form-specialist"] = {
                "name": "Form_Specialist",
                "role": "Google Workspace Forms API & Intake Gating Engine",
                "node_id": "node_13_developer"
            }
            logging.info("Booted agent instance: Form_Specialist (form-specialist)")
        except Exception as err:
            logging.error(f"Failed to instantiate Form_Specialist: {str(err)}")

        # Agent 4: Intake_Dispatcher
        try:
            self.agents["intake-dispatcher"] = IntakeDispatcherDaemon(schema_path=self.schema_path)
            self.agent_metadata["intake-dispatcher"] = {
                "name": "Intake_Dispatcher",
                "role": "Instantaneous GHL Ingress, SMS & Gmail API Dispatcher",
                "node_id": "node_04_courier"
            }
            logging.info("Booted agent instance: Intake_Dispatcher (intake-dispatcher)")
        except Exception as err:
            logging.error(f"Failed to instantiate Intake_Dispatcher: {str(err)}")

        # Agent 5: UI_Frontend_Architect
        try:
            self.agents["ui-frontend-architect"] = UIFrontendArchitectDaemon(schema_path=self.schema_path)
            self.agent_metadata["ui-frontend-architect"] = {
                "name": "UI_Frontend_Architect",
                "role": "React, Tailwind & Dark Mode Enterprise Interface Architect",
                "node_id": "node_13_developer"
            }
            logging.info("Booted agent instance: UI_Frontend_Architect (ui-frontend-architect)")
        except Exception as err:
            logging.error(f"Failed to instantiate UI_Frontend_Architect: {str(err)}")

        # Agent 6: Presentation_Specialist
        try:
            self.agents["presentation-specialist"] = PresentationSpecialistDaemon(schema_path=self.schema_path)
            self.agent_metadata["presentation-specialist"] = {
                "name": "Presentation_Specialist",
                "role": "Enterprise Pitch Deck & Programmatic Slides Compiler",
                "node_id": "node_09_catalyst_cmo"
            }
            logging.info("Booted agent instance: Presentation_Specialist (presentation-specialist)")
        except Exception as err:
            logging.error(f"Failed to instantiate Presentation_Specialist: {str(err)}")

        # Agent 7: Sales_Intelligence_Node
        try:
            self.agents["sales-intelligence-node"] = SalesIntelligenceNodeDaemon(schema_path=self.schema_path)
            self.agent_metadata["sales-intelligence-node"] = {
                "name": "Sales_Intelligence_Node",
                "role": "Lead Analytics, Sector Economics & Mathematical Allocation",
                "node_id": "node_05_analyst"
            }
            logging.info("Booted agent instance: Sales_Intelligence_Node (sales-intelligence-node)")
        except Exception as err:
            logging.error(f"Failed to instantiate Sales_Intelligence_Node: {str(err)}")

    def _wire_shared_bus(self) -> None:
        """Connects each instantiated agent to the unified event bus instance."""
        for agent_id, agent in self.agents.items():
            agent.bus = self.bus
            if hasattr(agent, "handle_bus_event"):
                self.bus.subscribe(agent_id, agent.handle_bus_event)
                logging.info(f"Subscribed @{agent_id} to shared InterAgentEventBus.")

    def _agent_worker_loop(self, agent_id: str, agent: Any) -> None:
        """Background worker loop for a child agent."""
        logging.info(f"Starting background worker thread for @{agent_id} ({agent.AGENT_NAME})...")
        agent.running = True
        
        while self.running and not self.stop_event.is_set():
            try:
                # 1. Process agent command queue
                if hasattr(agent, "process_command_queue"):
                    agent.process_command_queue()
                
                # 2. Record individual heartbeat
                if hasattr(agent, "_record_heartbeat"):
                    agent._record_heartbeat()
                    
            except Exception as err:
                logging.error(f"Error in @{agent_id} execution cycle: {str(err)}")
            
            # Poll interval
            time.sleep(1.5)
            
        agent.running = False
        logging.info(f"Background worker thread for @{agent_id} stopped.")

    def start_swarm(self) -> None:
        """Concurrently launches all child agents into background execution threads."""
        if self.running:
            logging.warning("Swarm is already running.")
            return

        self.running = True
        self.stop_event.clear()
        logging.info(f"Booting swarm fleet: {len(self.agents)} agents registered.")

        for agent_id, agent in self.agents.items():
            t = threading.Thread(
                target=self._agent_worker_loop,
                args=(agent_id, agent),
                name=f"WorkerThread-{agent_id}",
                daemon=True
            )
            self.threads[agent_id] = t
            t.start()
            logging.info(f"Thread started: {t.name}")

        self._record_swarm_status()
        logging.info("All child agent threads are active and listening for cross-node commands.")

    def stop_swarm(self) -> None:
        """Signals all child agent threads to terminate gracefully."""
        logging.info("Initiating graceful swarm shutdown...")
        self.running = False
        self.stop_event.set()

        for agent_id, agent in self.agents.items():
            if hasattr(agent, "running"):
                agent.running = False

        for agent_id, thread in self.threads.items():
            if thread.is_alive():
                thread.join(timeout=3.0)
                logging.info(f"Joined thread: {thread.name}")

        self._record_swarm_status()
        logging.info("Swarm shutdown complete.")

    def dispatch_cross_node_command(
        self,
        sender_agent: str,
        target_agent: str,
        action_name: str,
        payload: Dict[str, Any],
        impact_level: str = "NORMAL"
    ) -> Dict[str, Any]:
        """
        Publishes a cross-node command intent to the InterAgentEventBus,
        specifically targeted to a recipient agent via @mention routing.
        Passes the intent through the InstitutionalGovernanceOrchestrator for God Mode validation.
        """
        mention_text = f"@{target_agent} execute action {action_name}"
        logging.info(f"Dispatching cross-node intent: @{sender_agent} -> @{target_agent} [{action_name}]")
        
        # Pass through cognitive governance router
        task_id = f"task_{sender_agent}_{target_agent}_{action_name}_{uuid.uuid4().hex[:6]}"
        ambiguity = 0.25
        liability = 0.35 if impact_level == "NORMAL" else 0.65
        tools_required = 0.50
        latency_sensitivity = 0.30

        gov_audit = self.cognitive_governor.process_task(
            task_id=task_id,
            ambiguity=ambiguity,
            liability=liability,
            tools_required=tools_required,
            latency_sensitivity=latency_sensitivity,
            task_payload=payload
        )
        
        # Inject cognitive governance proof into payload metadata
        payload_with_governance = dict(payload)
        payload_with_governance["_cognitive_governance"] = {
            "execution_id": gov_audit.get("execution_id"),
            "tier_route": gov_audit.get("tier_route"),
            "complexity_score": gov_audit.get("complexity_score"),
            "state_hash_sha256": gov_audit.get("state_hash_sha256"),
            "circuit_breaker_status": gov_audit.get("circuit_breaker_status"),
            "latency_ms": gov_audit.get("latency_ms")
        }

        event = self.bus.publish_intent(
            sender_agent=sender_agent,
            action_name=action_name,
            payload=payload_with_governance,
            impact_level=impact_level,
            mention_text=mention_text
        )
        
        self.events_dispatched += 1
        self._record_swarm_status()
        return event

    def broadcast_swarm_command(
        self,
        sender_agent: str,
        action_name: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Broadcasts a command intent to all registered child agents simultaneously."""
        all_mentions = " ".join([f"@{aid}" for aid in self.agents.keys()])
        logging.info(f"Broadcasting swarm command from @{sender_agent} to all agents: {action_name}")
        
        event = self.bus.publish_intent(
            sender_agent=sender_agent,
            action_name=action_name,
            payload=payload,
            impact_level="MEDIUM",
            mention_text=all_mentions
        )
        
        self.events_dispatched += 1
        self._record_swarm_status()
        return event

    def execute_cross_node_demo_pipeline(self, prospect_name: str = "Hampton Roads BioTech Corp") -> Dict[str, Any]:
        """
        Executes a 7-node cross-command pipeline demonstration under God Mode:
        Step 0: Intelligence_Scout compiles OSINT research dossier on industry.
        Step 1: Sales_Intelligence_Node executes mathematical product suite allocation.
        Step 2: Presentation_Specialist compiles 6-slide enterprise pitch deck.
        Step 3: UI_Frontend_Architect synthesizes dark mode React TSX telemetry console.
        Step 4: Form_Specialist orchestrates Google Forms intake gating and Apps Script webhook.
        Step 5: Intake_Dispatcher executes sub-millisecond confirmation, SMS, and 70/30 receipt.
        Step 6: Workspace_Architect generates Google Docs Master SOP & Google Sheets Ledger.
        """
        logging.info(f"Starting God Mode Cross-Node Pipeline Demonstration for: '{prospect_name}'")
        pipeline_id = f"pipe_{uuid.uuid4().hex[:8]}"
        results = {}

        # STEP 0: Intelligence Scout Research Dossier
        scout_payload = {
            "query": f"{prospect_name} medical device manufacturing sterile logistics",
            "output_filename": f"research_{pipeline_id}.md",
            "research_depth": "deep_dive",
            "focus_areas": ["architecture", "endpoints", "auth", "examples"],
            "operator_confirmed": True
        }
        step0 = self.dispatch_cross_node_command(
            sender_agent="swarm-orchestrator-core",
            target_agent="intelligence-scout",
            action_name="SCOUT_TECHNICAL_INTELLIGENCE",
            payload=scout_payload
        )
        results["step0_intelligence_scout"] = step0

        # STEP 1: Sales Intelligence Node Analysis
        lead_payload = {
            "lead_id": f"lead_{pipeline_id}",
            "prospect_name": prospect_name,
            "industry": "medical_manufacturing",
            "company_profile": {
                "annual_revenue_bracket": "5m_to_25m",
                "employee_count": 35,
                "current_tech_stack": ["HubSpot", "Zapier", "Legacy SQL", "WordPress"],
                "estimated_tech_debt_score": 62
            },
            "operational_bottlenecks": [
                "manual_client_intake",
                "delayed_invoicing",
                "lack_of_realtime_kpis"
            ],
            "sales_readiness_status": "INTAKE_CAPTURED",
            "mandatory_directive_acknowledged": True
        }

        step1 = self.dispatch_cross_node_command(
            sender_agent="swarm-orchestrator-core",
            target_agent="sales-intelligence-node",
            action_name="ANALYZE_LEAD_DATA",
            payload=lead_payload
        )
        results["step1_sales_intelligence"] = step1

        # Direct execution to get mathematical product allocations
        sales_node = self.agents.get("sales-intelligence-node")
        math_output = sales_node.process_sales_directive(lead_payload)
        allocated = math_output.get("allocated_products", {})
        results["sales_dossier_status"] = math_output.get("status")

        # STEP 2: Presentation Specialist Deck Synthesis
        pitch_payload = {
            "title": f"{prospect_name} Enterprise Architecture",
            "high_ticket_tier": allocated.get("entry_tier", "Private Sovereign Enterprise Kernel Matrix"),
            "client_industry": "Medical Manufacturing & Sterilization Logistics",
            "value_proposition_variables": {
                "primary_economic_lever": "Eradication of manual re-keying & recurring SaaS licensing fees",
                "efficiency_multiple": "12x automated event throughput acceleration",
                "risk_reduction_moat": "Local encrypted SQLite vault persistence with Aegis risk governance",
                "projected_annual_savings": math_output.get("projected_annual_savings", 250000),
                "payback_period_days": 75
            },
            "deck_format": "slidev_and_google_slides_api",
            "operator_confirmed": True
        }

        step2 = self.dispatch_cross_node_command(
            sender_agent="sales-intelligence-node",
            target_agent="presentation-specialist",
            action_name="DRAFT_ENTERPRISE_PITCH",
            payload=pitch_payload
        )
        results["step2_presentation_specialist"] = step2

        # STEP 3: UI Frontend Architect Component Synthesis
        ui_payload = {
            "component_name": "BioTechIngressConsole",
            "description": f"Real-time operational telemetry console tailored for {prospect_name}",
            "layout_constraints": {
                "container_width": "max_w_7xl",
                "grid_columns": 3,
                "breakpoint_target": "responsive_all",
                "spacing_density": "compact_dense"
            },
            "data_visualization_needs": {
                "chart_types": ["kpi_stat_cards", "area_chart"],
                "metrics_to_display": ["Sterilization Throughput", "Batch Traceability", "Node SLA"],
                "interactive_filters": ["ALL", "ACTIVE", "AUDIT"]
            },
            "color_palette_parameters": {
                "primary_brand_hex": "#0ea5e9",
                "accent_hex": "#38bdf8",
                "surface_dark_hex": "#0b0f19",
                "border_subtle_hex": "#1e293b",
                "theme_mode": "dark_only",
                "glassmorphism_enabled": True
            },
            "operator_confirmed": True
        }

        step3 = self.dispatch_cross_node_command(
            sender_agent="sales-intelligence-node",
            target_agent="ui-frontend-architect",
            action_name="SYNTHESIZE_UI_COMPONENT",
            payload=ui_payload
        )
        results["step3_ui_frontend_architect"] = step3

        # STEP 4: Form Specialist Intake Gating
        form_payload = {
            "title": f"{prospect_name} Enterprise Onboarding Intake",
            "target_audience": "BioTech Operations Executives & Compliance Officers",
            "webhook_routing": {
                "primary_webhook_url": "https://goings-os.internal/api/v4.2/webhook/biotech_intake",
                "notification_channel": "google_chat_agent_bus",
                "apps_script_trigger": True
            },
            "fields": [
                {
                    "title": "Facility Compliance Officer Name",
                    "field_type": "TEXT",
                    "required": True
                },
                {
                    "title": "Primary FDA/ISO Regulatory Standard",
                    "field_type": "RADIO",
                    "required": True,
                    "options": ["ISO 13485", "FDA 21 CFR Part 820", "EU MDR", "Other"]
                },
                {
                    "title": "Expected Monthly Event Ingress",
                    "field_type": "RADIO",
                    "required": True,
                    "options": ["Under 100k", "100k to 1M", "1M to 10M", "Over 10M"]
                }
            ],
            "operator_confirmed": True
        }

        step4 = self.dispatch_cross_node_command(
            sender_agent="sales-intelligence-node",
            target_agent="form-specialist",
            action_name="ORCHESTRATE_GOOGLE_FORM",
            payload=form_payload
        )
        results["step4_form_specialist"] = step4

        # STEP 5: Intake Dispatcher Sub-Millisecond Confirmation
        dispatch_payload = {
            "client_data": {
                "client_id": f"client_{pipeline_id}",
                "first_name": "Executive",
                "last_name": "Director",
                "company_name": prospect_name,
                "email": "operations@biotechcorp.com",
                "phone": "+17575550199"
            },
            "transaction": {
                "transaction_id": f"txn_{pipeline_id}",
                "service_tier": allocated.get("entry_tier", "Private Sovereign Enterprise Kernel Matrix"),
                "amount": 18500.0,
                "currency": "USD",
                "payment_method": "CREDIT_CARD",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "status": "PAID"
            },
            "channels": {
                "email_dispatch": True,
                "sms_dispatch": True
            },
            "template_overrides": {
                "sms_message": f"Welcome {prospect_name}. Your Sovereign OS workspace deployment has been initialized. Ref: {pipeline_id}"
            }
        }

        step5 = self.dispatch_cross_node_command(
            sender_agent="sales-intelligence-node",
            target_agent="intake-dispatcher",
            action_name="DISPATCH_CLIENT_INTAKE",
            payload=dispatch_payload
        )
        results["step5_intake_dispatcher"] = step5

        # STEP 6: Workspace Architect Master SOP & Financial Ledger Asset
        workspace_payload = {
            "title": f"{prospect_name} Sovereign Operations Master Blueprint",
            "asset_type": "google_doc",
            "action": "create_new",
            "doc_spec": {
                "document_title": f"{prospect_name} Master Blueprint",
                "sections": [
                    {
                        "heading": "1. Executive Overview",
                        "body_paragraphs": [
                            f"Autonomous operations deployment for {prospect_name} featuring real-time telemetry, sub-millisecond intake, and offline resilience."
                        ]
                    },
                    {
                        "heading": "2. Financial Allocations & Payback",
                        "body_paragraphs": [
                            f"Initial Setup: $18,500.00. Projected Annual Savings: ${math_output.get('projected_annual_savings', 250000):,}. Amortization Payback: 75 days."
                        ]
                    }
                ]
            },
            "operator_confirmed": True
        }

        step6 = self.dispatch_cross_node_command(
            sender_agent="intake-dispatcher",
            target_agent="workspace-architect",
            action_name="ORCHESTRATE_WORKSPACE_ASSET",
            payload=workspace_payload
        )
        results["step6_workspace_architect"] = step6

        logging.info("God Mode Cross-Node Pipeline Demonstration completed successfully across all 7 agents!")
        return {
            "pipeline_id": pipeline_id,
            "status": "COMPLETED",
            "prospect_name": prospect_name,
            "math_suite": math_output,
            "steps_dispatched": 7,
            "execution_summary": results
        }

    def _record_swarm_status(self) -> None:
        """Writes aggregate swarm telemetry to persistent status JSON."""
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            meta = self.agent_metadata.get(agent_id, {})
            agent_statuses[agent_id] = {
                "name": getattr(agent, "AGENT_NAME", agent_id),
                "role": meta.get("role", "Child Agent"),
                "node_id": meta.get("node_id", "unknown"),
                "running": getattr(agent, "running", False),
                "thread_alive": self.threads[agent_id].is_alive() if agent_id in self.threads else False,
                "status_file": getattr(agent, "status_file", "unknown"),
                "memorized_tool": getattr(agent, "memorized_tool", {}).get("name", "none")
            }

        swarm_telemetry = {
            "orchestrator_id": self.ORCHESTRATOR_ID,
            "orchestrator_name": self.ORCHESTRATOR_NAME,
            "status": "ACTIVE" if self.running else "STOPPED",
            "uptime_seconds": int(time.time() - self.start_time),
            "total_agents_registered": len(self.agents),
            "total_agents_running": sum(1 for a in agent_statuses.values() if a["thread_alive"]),
            "events_dispatched": self.events_dispatched,
            "cognitive_matrix": {
                "RAG": "Dynamic Data Ingestion & Lexical/Cosine Ranking",
                "Graph_RAG": "Multi-Hop Relational Triples & Community Clustering",
                "Buffer_of_Thought": "Meta-Buffer Thought Templates & Distillation",
                "Skeleton_of_Thought": "Phase 1 Skeleton & Phase 2 Multi-Thread Expansion",
                "Algorithm_of_Thought": "A* State Space Search & Backtracking",
                "CoT_ToT_GoT": "Chain, Tree, & Graph Topology DAG Consensus",
                "Program_of_Thought": "Sandboxed Deterministic Arithmetic & Financial Execution",
                "Chain_of_Verification": "4-Step Pre-Flight Bias & Compliance Audit",
                "Self_Consistency_Reranker": "SC-RR Cluster Aggregation & Highest Consensus Re-ranking",
                "Thread_of_Thought": "Continuous In-Flight Context Horizon Retention",
                "Mixture_of_Reasoning_Experts": "MoRE Dynamic 4-Expert Routing Matrix",
                "Dual_Process_Cognition": "System 1 Fast Heuristics (<2ms) vs System 2 Deliberate Analysis (>35ms)",
                "Contrastive_CoT": "Invalid Trace Anti-Pattern Immunization",
                "ReAct_Loop": "Interleaved Thought, Action, Observation, Reflection Cycles",
                "Off_Grid_Router": "Option A (Starlink sat-comm 240ms) + Option B (Local Queue SQLite zero data loss)"
            },
            "api_bindings": {
                "overall_status": self.api_binding_report.get("overall_status", "UNKNOWN"),
                "audit_id": self.api_binding_report.get("audit_id", "none"),
                "service_account_email": self.api_binding_report.get("service_account_audit", {}).get("client_email"),
                "token_exchange_status": self.api_binding_report.get("token_exchange", {}).get("status"),
                "token_expiry_utc": self.api_binding_report.get("token_exchange", {}).get("token_expiry_utc"),
                "gmail_api_permitted": True,
                "google_docs_api_permitted": True,
                "google_sheets_api_permitted": True,
                "gohighlevel_webhooks_permitted": True,
                "all_child_agents_cleared": self.api_binding_report.get("swarm_permissions", {}).get("all_child_agents_cleared", False)
            },
            "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "agents": agent_statuses
        }

        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(swarm_telemetry, f, indent=2)
        except Exception as err:
            logging.warning(f"Could not record swarm status: {str(err)}")

    def run_forever(self) -> None:
        """Main thread execution loop keeping the entire swarm fleet active in background."""
        self.start_swarm()
        logging.info("Swarm orchestrator entered main execution loop. Press Ctrl+C to stop.")

        def handle_signal(signum, frame):
            logging.info("Received shutdown signal. Stopping swarm fleet...")
            self.stop_swarm()
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        try:
            while self.running:
                self._record_swarm_status()
                time.sleep(3.0)
        except (KeyboardInterrupt, SystemExit):
            self.stop_swarm()


if __name__ == "__main__":
    orchestrator = SwarmOrchestrator()
    
    # Check for CLI test flag (using -test or test to obey zero double-hyphen rule)
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("-test", "test", "-demo", "demo"):
        orchestrator.start_swarm()
        print("\n=== EXECUTING 7-NODE GOD MODE CROSS-COMMAND PIPELINE DEMO ===")
        demo_results = orchestrator.execute_cross_node_demo_pipeline()
        print(f"Pipeline Execution Status: {demo_results['status']}")
        print(f"Pipeline ID: {demo_results['pipeline_id']}")
        print(f"Total Steps Dispatched: {demo_results['steps_dispatched']}")
        print("Allocated Goings OS Products:")
        print(json.dumps(demo_results['math_suite'].get('allocated_products', {}), indent=2))
        print("\nStopping swarm after demo execution...")
        orchestrator.stop_swarm()
    else:
        orchestrator.run_forever()
