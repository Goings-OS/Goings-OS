# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: PRESENTATION SPECIALIST PERSISTENT CHILD AGENT (core_nodes/presentation_specialist_daemon.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; MANDATORY PITCH INTAKE GATING
# ==============================================================================

import os
import sys
import json
import time
import uuid
import signal
import logging
from typing import Dict, Any, Optional, List

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from core_nodes.node_20_agent_bus.agent_bus import (
    InterAgentEventBus,
    STANDARD_AGENT_CARDS
)
from core_nodes.cognitive_kernel import bind_child_agent_to_god_mode

# Configure logging
LOG_DIR = os.path.join(WORKSPACE_ROOT, "data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "presentation_specialist.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Presentation_Specialist] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)


class PresentationSpecialistDaemon:
    """
    Persistent Child Agent: Presentation_Specialist.
    Memorizes the orchestrate_enterprise_presentation MCP tool schema.
    Programmatically drafts enterprise pitch decks and Google Slides.
    MANDATORY DIRECTIVE: Before drafting, it must ask the operator for the specific
    high-ticket tier being pitched, the client industry, and the exact value proposition
    variables required for the presentation.
    """

    AGENT_ID = "presentation-specialist"
    AGENT_NAME = "Presentation_Specialist"

    def __init__(self, schema_path: Optional[str] = None):
        self.workspace_root = WORKSPACE_ROOT
        self.schema_path = schema_path or os.path.join(self.workspace_root, "mcp_registry_schema.json")
        self.presentations_dir = os.path.join(self.workspace_root, "data", "presentations")
        self.queue_dir = os.path.join(self.workspace_root, "data", "presentation_specialist_queue")
        self.status_file = os.path.join(self.workspace_root, "data", "presentation_specialist_status.json")
        os.makedirs(self.presentations_dir, exist_ok=True)
        os.makedirs(self.queue_dir, exist_ok=True)

        self.running = False
        self.start_time = time.time()
        self.decks_generated = 0
        self.gated_interviews_logged = 0
        self.memorized_schema: Dict[str, Any] = {}
        self.memorized_tool: Dict[str, Any] = {}
        self.memorized_parameters: Dict[str, Any] = {}
        self.required_parameters: list = []

        # Read and memorize schema immediately upon startup
        self.memorize_registry_schema()

        # Connect to inter-agent event bus
        self.bus = InterAgentEventBus(agent_cards=STANDARD_AGENT_CARDS)
        self.bus.subscribe(self.AGENT_ID, self.handle_bus_event)

        # Structurally bind to 15+ advanced AI cognitive frameworks & Option A/B failsafes
        bind_child_agent_to_god_mode(self, self.AGENT_ID)

    def memorize_registry_schema(self) -> None:
        """Reads mcp_registry_schema.json and internalizes orchestrate_enterprise_presentation parameters."""
        logging.info(f"Reading MCP registry schema from: {self.schema_path}")
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"MCP registry schema not found at {self.schema_path}")

        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.memorized_schema = json.load(f)

        target_tool = None
        for tool in self.memorized_schema.get("tools", []):
            if tool.get("name") == "orchestrate_enterprise_presentation":
                target_tool = tool
                break

        if not target_tool:
            raise ValueError("Tool 'orchestrate_enterprise_presentation' not found in mcp_registry_schema.json")

        self.memorized_tool = target_tool
        params = target_tool.get("parameters", {})
        self.memorized_parameters = params.get("properties", {})
        self.required_parameters = params.get("required", [])

        logging.info("SUCCESS: Schema successfully memorized for 'orchestrate_enterprise_presentation'")
        logging.info(f"Memorized top-level parameters: {list(self.memorized_parameters.keys())}")
        logging.info(f"Mandatory parameters: {self.required_parameters}")
        logging.info("MANDATORY DIRECTIVE ACTIVE: Pitch deck intake interview gating is ENGAGED.")

    def handle_bus_event(self, event: Dict[str, Any]) -> None:
        """Callback triggered when an event or mention arrives on the agent bus."""
        action = event.get("action_name")
        sender = event.get("sender_agent", "unknown")
        payload = event.get("payload", {})
        intent_id = event.get("intent_id", "none")

        logging.info(f"Inbound bus event received from @{sender}: action={action}, intent={intent_id}")

        if action in ("DRAFT_ENTERPRISE_PITCH", "ORCHESTRATE_GOOGLE_SLIDES", "SOLICIT_PITCH_VARIABLES"):
            try:
                result = self.process_pitch_directive(payload)
                logging.info(f"Pitch directive processed for intent {intent_id}: status={result.get('status')}")
            except Exception as err:
                logging.error(f"Error handling pitch directive {intent_id}: {str(err)}")

    def build_operator_interview(self, title: str = "Enterprise Pitch Deck") -> str:
        """Constructs the mandatory structured interview for the operator."""
        lines = [
            f"# 📋 Operator Intake Interview: {title}",
            "",
            "> ### 🚨 MANDATORY DIRECTIVE GATING",
            "> Before drafting this presentation, you must confirm the following 3 requirements.",
            "> Deck generation is paused until these variables are confirmed.",
            "",
            "---",
            "",
            "### 1. Specific High-Ticket Tier Being Pitched",
            "What exact engagement tier is being proposed to this client?",
            "- [$25,000 Private AI Implementation Sprint]",
            "- [$50,000 Sovereign OS Infrastructure Build]",
            "- [$100,000 Enterprise Autonomous Node Deployment]",
            "- [$250,000 Conglomerate Retainer & Strategic Governance]",
            "",
            "### 2. Target Client Industry",
            "What is the client's industry sector?",
            "(e.g., Private Equity, Commercial Real Estate, Healthcare Systems, Boutique Legal, Luxury Hospitality)",
            "",
            "### 3. Exact Value Proposition Variables",
            "- Primary Economic Lever: (What exact financial cost is eliminated or revenue generated?)",
            "- Operational Velocity Multiple: (e.g., 5x, 10x, or 20x acceleration in core workflows)",
            "- Risk Reduction Moat: (e.g., On-premise KMS encryption, zero third-party AI data leaks)",
            "- Projected Annual Savings: ($ amount in USD)",
            "- Amortization Payback Period: (e.g., 60 days, 90 days, 6 months)",
            ""
        ]
        return "\n".join(lines)

    def process_pitch_directive(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforces the mandatory operator directive before executing deck compilation.
        """
        title = payload.get("title", "Enterprise Pitch Deck")
        confirmed = payload.get("operator_confirmed", False)
        tier = payload.get("high_ticket_tier")
        industry = payload.get("client_industry")
        value_vars = payload.get("value_proposition_variables", {})

        # CHECK MANDATORY DIRECTIVE
        has_value_vars = bool(value_vars.get("primary_economic_lever") and value_vars.get("efficiency_multiple"))
        if not confirmed or not tier or not industry or not has_value_vars:
            logging.warning(f"MANDATORY DIRECTIVE BLOCKED: Operator confirmation missing for '{title}'. Gating execution.")
            interview_content = self.build_operator_interview(title)
            gate_id = f"gated_{uuid.uuid4().hex[:8]}"
            gate_file = os.path.join(self.presentations_dir, f"{gate_id}_{title.replace(' ', '_')}_interview.md")

            with open(gate_file, "w", encoding="utf-8") as f:
                f.write(interview_content)

            self.gated_interviews_logged += 1
            self._record_heartbeat()

            return {
                "status": "GATED_AWAITING_OPERATOR_INPUT",
                "gate_id": gate_id,
                "message": "Mandatory operator interview dispatched. Awaiting high-ticket tier, industry, and value prop variables.",
                "interview_file": gate_file,
                "missing_dimensions": [
                    k for k, v in {
                        "high_ticket_tier": bool(tier),
                        "client_industry": bool(industry),
                        "value_proposition_variables": has_value_vars,
                        "operator_confirmed": bool(confirmed)
                    }.items() if not v
                ]
            }

        # OPERATOR CONFIRMED: Proceed to draft enterprise pitch deck
        task_id = f"task_deck_{uuid.uuid4().hex[:8]}"
        if hasattr(self, "execute_with_god_mode"):
            god_mode_result = self.execute_with_god_mode(
                task_id=task_id,
                action_name="DRAFT_ENTERPRISE_PITCH",
                payload=payload,
                executor_func=self._generate_presentation_bundle
            )
            return god_mode_result["output"]
        return self._generate_presentation_bundle(payload)

    def _generate_presentation_bundle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesizes the complete Google Slides API v1 spec, Slidev deck, and manifest."""
        title = payload["title"]
        tier = payload["high_ticket_tier"]
        industry = payload["client_industry"]
        value_vars = payload["value_proposition_variables"]
        styling = payload.get("styling", {})
        primary_hex = styling.get("primary_hex", "#1B365D")
        accent_hex = styling.get("accent_hex", "#C5A059")

        deck_id = f"deck_{uuid.uuid4().hex[:10]}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

        logging.info(f"Drafting enterprise pitch deck: '{title}' [{tier} | {industry}] [ID: {deck_id}]")

        # 1. Slidev / Markdown Presentation Deck
        slidev_content = f"""---
theme: default
background: '{primary_hex}'
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
title: {title}
---

# {title}
### {tier} Implementation for {industry}

<div class="pt-12">
  <span class="px-4 py-2 rounded text-white bg-opacity-20 bg-white border border-yellow-500 font-mono">
    CONFIDENTIAL STRATEGIC PROPOSAL // {timestamp}
  </span>
</div>

---
layout: default
---

# Executive Dilemma: Legacy Friction in {industry}

The prevailing enterprise operational model imposes unsustainable friction:

* **Fragmented SaaS Tax:** Continuous subscription bleed across disparate cloud portals.
* **Throughput Bottlenecks:** Human latency across document review, compliance auditing, and reporting.
* **Sovereignty Risks:** Sensitive enterprise telemetry leaked to external third-party model hosts.

> **Industry Context:** In {industry}, latency translates directly into lost margin and statutory exposure.

---
layout: default
---

# The Sovereign OS Architectural Solution

Keep It Goings Consulting delivers an isolated, autonomous private architecture:

* **Private Node Fleet:** Autonomous child agents specialized for ingress, research, and workspace asset generation.
* **On-Premise Vault Security:** Zero-SaaS state stored in encrypted SQLite vaults with KMS key isolation.
* **Strict Compliance Engine:** Zero typographical em-dashes and zero circular deadlock arbitration.

---
layout: two-cols
---

# Financial Modeling & Strategic ROI

### Economic Value Proposition
* **Primary Economic Lever:** {value_vars.get('primary_economic_lever')}
* **Operational Multiplier:** {value_vars.get('efficiency_multiple')}
* **Security & Governance Moat:** {value_vars.get('risk_reduction_moat', '100% Private Cloud KMS Isolation')}

::right::

<div class="p-6 rounded-lg bg-gray-900 border border-gray-700 text-white ml-4">
  <h3 class="text-yellow-400 font-bold mb-4">Investment & Payback Summary</h3>
  <p class="text-sm text-gray-300">Target Proposal Tier:</p>
  <p class="text-2xl font-bold text-white mb-4">{tier}</p>
  <p class="text-sm text-gray-300">Projected Annual Savings:</p>
  <p class="text-2xl font-bold text-green-400 mb-4">${value_vars.get('projected_annual_savings', 180000):,.2f}</p>
  <p class="text-sm text-gray-300">Amortization Horizon:</p>
  <p class="text-lg font-bold text-yellow-300">{value_vars.get('payback_period_months', 3)} Months Payback</p>
</div>

---
layout: default
---

# Strategic 90-Day Execution Roadmap

* **Phase 1: Foundation & Vault Provisioning (Days 1 to 30)**
  Deploy private virtual environment, KMS root authority, and baseline ingress gateways.
* **Phase 2: Autonomous Agent Swarm Deployment (Days 31 to 60)**
  Activate Workspace_Architect, Form_Specialist, and Intake_Dispatcher nodes.
* **Phase 3: Production Hardening & Executive Handover (Days 61 to 90)**
  Full penetration test, disaster recovery drill, and executive staff operator certification.

---
layout: center
class: text-center
---

# Commercial Directive: {tier}

### Partnership Formalization & Next Directives

To initiate this implementation:
1. Counter-sign the Confidential Retainer Agreement.
2. Wire the initial milestone allocation to the designated treasury account.
3. Access your private repository and communication bridge.

<div class="mt-8 font-mono text-xs text-gray-400">
  KEEP IT GOINGS CONSULTING // GOINGS-OS ENTERPRISE ARCHITECTURE
</div>
"""

        # 2. Google Slides API v1 batchUpdate Specification
        slides_api_spec = {
            "createPresentation": {
                "title": f"[Goings-OS] {title} ({tier})"
            },
            "batchUpdate": {
                "requests": [
                    {
                        "createSlide": {
                            "insertionIndex": 0,
                            "slideLayout": {
                                "predefinedLayout": "TITLE"
                            }
                        }
                    },
                    {
                        "createSlide": {
                            "insertionIndex": 1,
                            "slideLayout": {
                                "predefinedLayout": "SECTION_HEADER"
                            }
                        }
                    },
                    {
                        "createSlide": {
                            "insertionIndex": 2,
                            "slideLayout": {
                                "predefinedLayout": "TITLE_AND_BODY"
                            }
                        }
                    },
                    {
                        "createSlide": {
                            "insertionIndex": 3,
                            "slideLayout": {
                                "predefinedLayout": "TITLE_AND_TWO_COLUMNS"
                            }
                        }
                    },
                    {
                        "createSlide": {
                            "insertionIndex": 4,
                            "slideLayout": {
                                "predefinedLayout": "TITLE_AND_BODY"
                            }
                        }
                    },
                    {
                        "createSlide": {
                            "insertionIndex": 5,
                            "slideLayout": {
                                "predefinedLayout": "BIG_NUMBER"
                            }
                        }
                    }
                ]
            },
            "metadata": {
                "deck_id": deck_id,
                "high_ticket_tier": tier,
                "client_industry": industry,
                "value_proposition_variables": value_vars,
                "styling": {
                    "primary_hex": primary_hex,
                    "accent_hex": accent_hex
                }
            }
        }

        # 3. Write files to data/presentations/
        clean_name = title.replace(" ", "_")
        deck_file = os.path.join(self.presentations_dir, f"{deck_id}_{clean_name}_deck.md")
        spec_file = os.path.join(self.presentations_dir, f"{deck_id}_{clean_name}_slides_api_spec.json")
        manifest_file = os.path.join(self.presentations_dir, f"{deck_id}_{clean_name}_manifest.md")

        with open(deck_file, "w", encoding="utf-8") as f:
            f.write(slidev_content)

        with open(spec_file, "w", encoding="utf-8") as f:
            json.dump(slides_api_spec, f, indent=2)

        manifest_lines = [
            f"# 📊 Pitch Deck Manifest: {title}",
            "",
            f"**Deck Identifier:** `{deck_id}`  ",
            f"**High-Ticket Tier:** `{tier}`  ",
            f"**Target Industry:** `{industry}`  ",
            f"**Economic Lever:** `{value_vars.get('primary_economic_lever')}`  ",
            f"**Efficiency Multiple:** `{value_vars.get('efficiency_multiple')}`  ",
            f"**Compiled Timestamp:** `{timestamp}`  ",
            "",
            "> ### 🔒 OPERATOR INTAKE CONFIRMED",
            "> Operator interview completed and certified. Full enterprise presentation deck drafted.",
            "",
            "---",
            "",
            "## 1. Generated Artifact Files",
            f"* **Slidev / Markdown Presentation:** `{deck_file}`",
            f"* **Google Slides API v1 Payload:** `{spec_file}`",
            f"* **Slide Count:** 6 Slides (Title, Dilemma, Solution, ROI Model, Roadmap, Commercial Directive)",
            "",
            "---",
            "",
            "## 2. Google Slides API Deployment Directive",
            "```bash",
            f"# Create presentation via Google Workspace Slides API",
            f"curl -X POST https://slides.googleapis.com/v1/presentations \\",
            f"  -H 'Authorization: Bearer $(gcloud auth print-access-token)' \\",
            f"  -H 'Content-Type: application/json' \\",
            f"  -d @{spec_file}",
            "```",
            ""
        ]

        with open(manifest_file, "w", encoding="utf-8") as f:
            f.write("\n".join(manifest_lines))

        self.decks_generated += 1
        self._record_heartbeat()
        logging.info(f"Presentation bundle written successfully: {manifest_file}")

        return {
            "status": "GENERATED",
            "deck_id": deck_id,
            "title": title,
            "deck_file": deck_file,
            "slides_api_spec": spec_file,
            "manifest_file": manifest_file
        }

    def process_command_queue(self) -> None:
        """Watches queue folder for presentation drafting jobs deposited by external agents."""
        for item in os.listdir(self.queue_dir):
            if item.endswith(".json") and not item.startswith(".") and not item.startswith("completed_") and not item.startswith("error_"):
                job_file = os.path.join(self.queue_dir, item)
                try:
                    with open(job_file, "r", encoding="utf-8") as f:
                        payload = json.load(f)
                    logging.info(f"Processing queued presentation job: {item}")
                    self.process_pitch_directive(payload)
                    done_file = os.path.join(self.queue_dir, f"completed_{item}")
                    os.rename(job_file, done_file)
                except Exception as err:
                    logging.error(f"Failed to process presentation job {item}: {str(err)}")
                    error_file = os.path.join(self.queue_dir, f"error_{item}")
                    try:
                        os.rename(job_file, error_file)
                    except Exception:
                        pass

    def _record_heartbeat(self) -> None:
        """Writes real-time status and telemetry to persistent status JSON."""
        status_data = {
            "agent_id": self.AGENT_ID,
            "agent_name": self.AGENT_NAME,
            "status": "ACTIVE" if self.running else "STOPPED",
            "mandatory_directive_active": True,
            "uptime_seconds": int(time.time() - self.start_time),
            "decks_generated": self.decks_generated,
            "gated_interviews_logged": self.gated_interviews_logged,
            "memorized_tool": "orchestrate_enterprise_presentation",
            "required_parameters": self.required_parameters,
            "supported_parameters": list(self.memorized_parameters.keys()),
            "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "presentations_directory": self.presentations_dir,
            "queue_directory": self.queue_dir
        }
        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2)
        except Exception as err:
            logging.warning(f"Could not record heartbeat: {str(err)}")

    def run_forever(self) -> None:
        """Runs the daemon loop continuously in the background."""
        self.running = True
        logging.info("Presentation_Specialist daemon loop started. Remaining active in background.")

        def shutdown(signum, frame):
            logging.info("Received shutdown signal. Gracefully exiting...")
            self.running = False

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        while self.running:
            self.process_command_queue()
            self._record_heartbeat()
            time.sleep(2.0)

        logging.info("Presentation_Specialist daemon stopped.")


if __name__ == "__main__":
    daemon = PresentationSpecialistDaemon()
    daemon.run_forever()
