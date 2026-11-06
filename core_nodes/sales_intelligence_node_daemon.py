# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: SALES INTELLIGENCE NODE PERSISTENT CHILD AGENT (core_nodes/sales_intelligence_node_daemon.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; MANDATORY PRE-ENGAGEMENT DOSSIER GATING
# ==============================================================================

import os
import sys
import json
import time
import math
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
LOG_FILE = os.path.join(LOG_DIR, "sales_intelligence_node.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Sales_Intelligence_Node] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)


class SalesIntelligenceNodeDaemon:
    """
    Persistent Child Agent: Sales_Intelligence_Node.
    Specializes in analyzing captured lead data and evaluating sector economics.
    MANDATORY DIRECTIVE: Before the sales team engages, this node must generate
    a dossier detailing the prospect's industry and mathematically output the precise
    Goings OS products (Entry tiers, Custom UIs, Websites) to pitch.
    """

    AGENT_ID = "sales-intelligence-node"
    AGENT_NAME = "Sales_Intelligence_Node"

    def __init__(self, schema_path: Optional[str] = None):
        self.workspace_root = WORKSPACE_ROOT
        self.schema_path = schema_path or os.path.join(self.workspace_root, "mcp_registry_schema.json")
        self.dossiers_dir = os.path.join(self.workspace_root, "data", "sales_dossiers")
        self.queue_dir = os.path.join(self.workspace_root, "data", "sales_intelligence_queue")
        self.status_file = os.path.join(self.workspace_root, "data", "sales_intelligence_status.json")
        os.makedirs(self.dossiers_dir, exist_ok=True)
        os.makedirs(self.queue_dir, exist_ok=True)

        self.running = False
        self.start_time = time.time()
        self.dossiers_compiled = 0
        self.embargoes_logged = 0
        self.memorized_schema: Dict[str, Any] = {}
        self.memorized_tool: Dict[str, Any] = {}
        self.memorized_parameters: Dict[str, Any] = {}
        self.required_parameters: list = []

        # Read and memorize schema immediately upon startup
        self.memorize_registry_schema()

        # Connect to inter-agent event bus
        try:
            self.bus = InterAgentEventBus(agent_cards=STANDARD_AGENT_CARDS)
            self.bus.subscribe(self.AGENT_ID, self.handle_bus_event)
            logging.info("InterAgentEventBus connected and subscribed for Sales_Intelligence_Node.")
        except Exception as err:
            logging.warning(f"Event bus initialization warning: {str(err)}")
            self.bus = None

        # Structurally bind to 15+ advanced AI cognitive frameworks & Option A/B failsafes
        bind_child_agent_to_god_mode(self, self.AGENT_ID)

        self._record_heartbeat()

    def handle_bus_event(self, event: Dict[str, Any]) -> None:
        """Callback triggered when an event or mention arrives on the agent bus."""
        action = event.get("action_name")
        sender = event.get("sender_agent", "unknown")
        payload = event.get("payload", {})
        intent_id = event.get("intent_id", "none")

        logging.info(f"Inbound bus event received from @{sender}: action={action}, intent={intent_id}")

        if action in ("ANALYZE_LEAD_DATA", "GENERATE_SALES_DOSSIER", "CALCULATE_PRODUCT_SUITE"):
            try:
                result = self.process_sales_directive(payload)
                logging.info(f"Sales directive processed for intent {intent_id}: status={result.get('status')}")
            except Exception as err:
                logging.error(f"Error handling sales directive {intent_id}: {str(err)}")

    def memorize_registry_schema(self) -> None:
        """Reads and memorizes the orchestrate_sales_intelligence tool schema."""
        logging.info(f"Reading MCP registry schema from: {self.schema_path}")
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema not found: {self.schema_path}")

        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.memorized_schema = json.load(f)

        tool_def = None
        for tool in self.memorized_schema.get("tools", []):
            if tool.get("name") == "orchestrate_sales_intelligence":
                tool_def = tool
                break

        if not tool_def:
            raise KeyError("Tool 'orchestrate_sales_intelligence' not found in mcp_registry_schema.json")

        self.memorized_tool = tool_def
        params = tool_def.get("parameters", {})
        self.memorized_parameters = params.get("properties", {})
        self.required_parameters = params.get("required", [])

        logging.info("SUCCESS: Schema successfully memorized for 'orchestrate_sales_intelligence'")
        logging.info(f"Memorized top-level parameters: {list(self.memorized_parameters.keys())}")
        logging.info(f"Mandatory parameters: {self.required_parameters}")
        logging.info("MANDATORY DIRECTIVE ACTIVE: Pre-engagement sales intelligence embargo is ENGAGED.")

    def calculate_mathematical_suite(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes deterministic mathematical allocation of Goings OS product suite.
        Calculates Entry Tier, Custom UI, and Website recommendations based on firmographics.
        """
        prospect_name = payload.get("prospect_name", "Enterprise Prospect")
        industry = payload.get("industry", "general_commercial").lower()
        profile = payload.get("company_profile", {})
        bottlenecks = payload.get("operational_bottlenecks", [])

        revenue_bracket = profile.get("annual_revenue_bracket", "250k_to_1m")
        employee_count = max(1, profile.get("employee_count", 10))
        tech_debt_score = max(0, min(100, profile.get("estimated_tech_debt_score", 50)))

        # 1. Revenue Multiplier (R_m)
        revenue_map = {
            "under_250k": 1.0,
            "250k_to_1m": 1.8,
            "1m_to_5m": 3.2,
            "5m_to_25m": 6.0,
            "over_25m": 10.0
        }
        r_m = revenue_map.get(revenue_bracket, 1.8)

        # 2. Tech Debt Coefficient (C_td)
        c_td = round(tech_debt_score / 100.0, 3)

        # 3. Headcount Scaling Factor (H_s)
        h_s = round(math.log10(employee_count) * 1.25, 3)

        # 4. Bottleneck Impact (B_i)
        b_i = round(len(bottlenecks) * 0.75, 3)

        # 5. Goings OS Suitability Index (S_gos)
        raw_suitability = 30.0 + (r_m * 4.0) + (c_td * 25.0) + (b_i * 5.0) + (h_s * 3.0)
        s_gos = min(100.0, round(raw_suitability, 1))

        # 6. Allocate Entry Tier
        if r_m <= 1.0:
            entry_tier = {
                "tier_code": "ENTRY_TIER_STARTER",
                "tier_name": "Sovereign Kernel Starter Matrix",
                "setup_price": 2970.0,
                "monthly_retainer": 297.0,
                "deliverables": [
                    "Automated Webhook Ingress (GHL & Custom Hooks)",
                    "Local SQLite Sovereign Vault Persistence",
                    "Dual-Write CRM Field Synchronization",
                    "Daily Automated Cron Health Check"
                ]
            }
        elif r_m <= 3.2:
            entry_tier = {
                "tier_code": "ENTRY_TIER_VELOCITY",
                "tier_name": "Automated Ingress & Dispatch Matrix (High Velocity)",
                "setup_price": 7500.0,
                "monthly_retainer": 497.0,
                "deliverables": [
                    "Sub-Millisecond SMS & Gmail Dispatch Engine",
                    "Google Forms API Operator Intake Gating",
                    "Forensic Google Sheets Ledger Synchronization",
                    "Twilio & Gmail API Infrastructure Hooks",
                    "Lead Qualification Scorecard Automation"
                ]
            }
        else:
            entry_tier = {
                "tier_code": "ENTRY_TIER_ENTERPRISE",
                "tier_name": "Private Sovereign Enterprise Kernel Matrix",
                "setup_price": 18500.0,
                "monthly_retainer": 1250.0,
                "deliverables": [
                    "9 Gems Cognitive Kernel Multi-Node Architecture",
                    "Aegis Risk Governance & Cryptographic Model Armor",
                    "Isolated Multi-Tenant Sandboxes with Local SQLite Vaults",
                    "Autonomous Self-Healing Cron Deployment Fleet",
                    "Regulatory Compliance & SOC-2 Audit Logging Engine"
                ]
            }

        # 7. Allocate Custom UI
        bot_set = set(bottlenecks)
        if any(term in industry for term in ["medical", "manufactur", "logistics", "supply_chain", "tech", "saas"]) or "lack_of_realtime_kpis" in bot_set:
            custom_ui = {
                "ui_code": "UI_TELEMETRY_CONSOLE",
                "ui_name": "Dark Mode Operational Telemetry Console (React + Tailwind)",
                "price": 12000.0,
                "tech_stack": "React 19, TypeScript, Tailwind CSS, Lucide Icons, Glassmorphism",
                "deliverables": [
                    "Real-Time Event Processing & Ingress Gauge Canvas",
                    "Dense Telemetry Metric Cards with Trend Velocity",
                    "Active Node Fleet Activity Stream with Heartbeat Status",
                    "Zero Em-Dash & Strict TypeScript Production Codebase",
                    "One-Click CSV / Audit Forensic Export Subsystem"
                ]
            }
        elif any(term in industry for term in ["fintech", "finance", "tax", "legal", "compliance", "real_estate"]) or "delayed_invoicing" in bot_set:
            custom_ui = {
                "ui_code": "UI_FINANCIAL_LEDGER",
                "ui_name": "Forensic Executive Financial Ledger Portal",
                "price": 15000.0,
                "tech_stack": "React 19, Tailwind CSS, Recharts, Cryptographic Ledger Hooks",
                "deliverables": [
                    "Revenue Waterfall & Ingress Reinvestment Visualizer",
                    "Cryptographic Split-Commission Automated Calculator",
                    "Corporate Tax Shielding & Statutory Compliance Badges",
                    "Multi-Currency Escrow & Settlement Verification Panel",
                    "Forensic Transaction Search & Ledger Reconciliation"
                ]
            }
        elif any(term in industry for term in ["maritime", "luxury", "hospitality", "event", "concierge", "vip"]) or "manual_client_intake" in bot_set:
            custom_ui = {
                "ui_code": "UI_VIP_CONCIERGE",
                "ui_name": "VIP Concierge High-Ticket Booking Portal",
                "price": 14000.0,
                "tech_stack": "React 19, Tailwind CSS, Signature Purple/Gold Palette, Stripe Gateway",
                "deliverables": [
                    "Bespoke High-Fidelity Cabin / Suite / Package Selector",
                    "Direct Whisper List VIP Priority Access Routing",
                    "Instant Stripe Deposit & High-Ticket Escrow Ingress",
                    "Interactive Itinerary & Executive Hospitality Timeline",
                    "Sub-Millisecond Onboarding Confirmation Delivery"
                ]
            }
        else:
            custom_ui = {
                "ui_code": "UI_IMPACT_GOVERNANCE",
                "ui_name": "Sovereign SOP & Impact Governance Dashboard",
                "price": 9500.0,
                "tech_stack": "React 19, Tailwind CSS, Google Workspace API Connectors",
                "deliverables": [
                    "Philanthropic Program & Grant Allocation Milestone Tracker",
                    "Volunteer & Client Intake Funnel Visualization",
                    "Automated Google Docs SOP Generation Conduit",
                    "Dual-Write Firebase & Master Vortex Sync Monitor",
                    "Executive Impact Reporting & Donor Transparency Ledger"
                ]
            }

        # 8. Allocate Website
        if r_m <= 1.8:
            website = {
                "website_code": "WEB_CONVERSION_ENGINE",
                "website_name": "Sovereign High-Converting Conversion Engine (Vite/React)",
                "price": 4500.0,
                "architecture": "Single-Page Reactive Hub with Sub-Second TTFB",
                "deliverables": [
                    "Dark-Mode High-Contrast Brand Showcase",
                    "Embedded Dynamic Lead Capture Conduit",
                    "Direct GoHighLevel Webhook Handshake",
                    "Lighthouse 98+ Performance Optimization",
                    "Full Mobile-Responsive Geometry & Micro-Interactions"
                ]
            }
        elif r_m <= 6.0:
            website = {
                "website_code": "WEB_OMNICHANNEL_PORTAL",
                "website_name": "Omnichannel 4-Pillar Enterprise Web Portal",
                "price": 9500.0,
                "architecture": "Sovereign Bridge V6 Multi-Node Industrial Architecture",
                "deliverables": [
                    "4 Distinct Node Portals with Branded Color Identities",
                    "Central Index Conduit with Digital Paper Submission Hub",
                    "Dual-Write Strategy (Firebase + Master Vortex GAS)",
                    "Sub-Account Dedicated Routing with Location ID Gating",
                    "Embedded Video & Dynamic YouTube Maker Component Sync"
                ]
            }
        else:
            website = {
                "website_code": "WEB_BESPOKE_ECOSYSTEM",
                "website_name": "Bespoke Multi-Tenant Sovereign Digital Ecosystem",
                "price": 22500.0,
                "architecture": "Headless Next.js Multi-Tenant Enterprise Architecture",
                "deliverables": [
                    "SSO & Role-Based Client Access Control (RBAC)",
                    "Multi-Region CDN with Sub-Millisecond Global Edge Caching",
                    "Dynamic Personalized Client Dashboards upon Sign-In",
                    "Complete Headless CMS & White-Glove Brand Asset Integration",
                    "Dedicated SLA & 24/7 Cognitive Kernel Health Telemetry"
                ]
            }

        # 9. Financial Summary & ROI Projections
        initial_setup = entry_tier["setup_price"] + custom_ui["price"] + website["price"]
        annual_maintenance = entry_tier["monthly_retainer"] * 12
        total_contract_value = initial_setup + annual_maintenance

        # Mathematical ROI Model:
        # Estimated cost savings = Headcount * $8,500 * Tech Debt + Bottlenecks * $14,000
        annual_labor_savings = int((employee_count * 8500.0 * c_td) + (len(bottlenecks) * 14000.0))
        net_annual_roi = annual_labor_savings - total_contract_value
        roi_percentage = round((net_annual_roi / max(total_contract_value, 1.0)) * 100.0, 1)
        payback_days = int(max(18, round((total_contract_value / max(annual_labor_savings, 1.0)) * 365.0, 0)))

        return {
            "prospect_name": prospect_name,
            "industry": industry,
            "math_factors": {
                "revenue_multiplier": r_m,
                "tech_debt_coefficient": c_td,
                "headcount_scaling": h_s,
                "bottleneck_impact": b_i,
                "suitability_index": s_gos
            },
            "allocated_products": {
                "entry_tier": entry_tier,
                "custom_ui": custom_ui,
                "website": website
            },
            "financial_summary": {
                "initial_implementation_investment": initial_setup,
                "annual_maintenance_retainer": annual_maintenance,
                "total_year_one_contract_value": total_contract_value,
                "projected_annual_labor_savings": annual_labor_savings,
                "net_annual_roi_value": net_annual_roi,
                "projected_roi_percentage": roi_percentage,
                "payback_period_days": payback_days
            }
        }

    def build_embargo_notice(self, lead_id: str, prospect_name: str, missing_fields: List[str]) -> str:
        """Constructs an official pre-engagement embargo notice when firmographics are incomplete."""
        lines = [
            f"# 🛑 PRE-ENGAGEMENT SALES INTELLIGENCE EMBARGO: {prospect_name}",
            "",
            "> ### 🚨 MANDATORY DIRECTIVE GATING ENFORCED",
            "> The sales team is **STRICTLY EMBARGOED** from contacting, pitching, or calling this prospect.",
            "> All outreach is held until captured lead data is complete and the mathematical sales dossier is generated.",
            "",
            "---",
            "",
            f"**Lead Identifier:** `{lead_id}`  ",
            f"**Prospect Name:** `{prospect_name}`  ",
            f"**Embargo Timestamp:** `{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}`  ",
            "",
            "## Missing Required Lead Parameters:",
            *[f"- ❌ `{field}`" for field in missing_fields],
            "",
            "## Required Action to Release Embargo:",
            "1. Collect missing firmographics (Annual Revenue Bracket, Employee Count, or Tech Debt Score).",
            "2. Update the lead record with `mandatory_directive_acknowledged: true`.",
            "3. Re-submit to `data/sales_intelligence_queue/` or execute `orchestrate_sales_intelligence`.",
            "",
            "---",
            "*Goings-OS Sales Governance Subsystem // Node 05 Analyst*"
        ]
        return "\n".join(lines)

    def generate_sales_dossier(self, payload: Dict[str, Any], math_res: Dict[str, Any]) -> Dict[str, str]:
        """
        Synthesizes the comprehensive markdown sales dossier and JSON telemetry file.
        Commits artifacts to data/sales_dossiers/.
        """
        lead_id = payload.get("lead_id", f"lead_{uuid.uuid4().hex[:8]}")
        prospect_name = math_res["prospect_name"]
        industry = math_res["industry"].replace("_", " ").title()
        factors = math_res["math_factors"]
        products = math_res["allocated_products"]
        fin = math_res["financial_summary"]
        profile = payload.get("company_profile", {})
        bottlenecks = payload.get("operational_bottlenecks", [])
        current_stack = profile.get("current_tech_stack", ["Standard Legacy Stack"])

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        slug = "".join([c if c.isalnum() else "_" for c in prospect_name.lower()]).strip("_")

        dossier_filename = f"dossier_{lead_id}_{slug}.md"
        dossier_path = os.path.join(self.dossiers_dir, dossier_filename)
        telemetry_filename = f"telemetry_{lead_id}_{slug}.json"
        telemetry_path = os.path.join(self.dossiers_dir, telemetry_filename)

        entry = products["entry_tier"]
        ui = products["custom_ui"]
        web = products["website"]

        # Build Industry Analysis paragraph based on sector
        industry_lower = industry.lower()
        if "medical" in industry_lower or "health" in industry_lower or "manufactur" in industry_lower:
            industry_context = (
                f"The {industry} landscape is defined by stringent FDA/ISO sterilization regulations, high-density telemetry "
                "requirements, and strict audit traceability. Traditional off-the-shelf CRMs leave massive gaps in batch-tracking "
                "and real-time equipment status, leading to compliance overhead and operator friction. Goings OS delivers "
                "air-gapped local vault persistence and deterministic event processing, ensuring zero regulatory leakage."
            )
            discovery_q = "How do you currently verify that machine telemetry feeds and batch records sync to your executive reporting without manual reconciliation?"
        elif "fin" in industry_lower or "tax" in industry_lower or "legal" in industry_lower:
            industry_context = (
                f"The {industry} vertical operates under intense scrutiny regarding data privacy, fiduciary ledger integrity, "
                "and multi-jurisdiction compliance. Cloud SaaS architectures create exposure to third-party data breaches and "
                "uncontrolled model training. Goings OS provides mathematical certainty via on-premise SQLite encrypted vaults "
                "and cryptographic split-commission ledgers."
            )
            discovery_q = "When transactions settle, how many minutes or days are lost manually recalculating fee splits and verifying escrow before disbursements?"
        elif "maritime" in industry_lower or "luxury" in industry_lower or "hospitality" in industry_lower:
            industry_context = (
                f"The {industry} sector relies on elite guest experiences, discrete concierge services, and high-converting "
                "visual authority. Standard booking funnels cause significant cart abandonment among high-net-worth clients. "
                "Goings OS integrates the Direct Whisper List protocol with tailored glassmorphic reservation portals for frictionless conversion."
            )
            discovery_q = "What percentage of VIP inquiries abandon standard booking forms before reaching your private concierge team?"
        else:
            industry_context = (
                f"Enterprises in {industry} encounter severe margin compression caused by fragmented SaaS subscriptions, "
                "manual data re-entry, and disjointed communication channels. Goings OS replaces multi-app chaos with a unified, "
                "autonomous kernel that executes sub-millisecond workflows with deterministic mathematical precision."
            )
            discovery_q = "If your client intake and dispatch executed in under 5 milliseconds instead of several hours, what immediate revenue lift would that unlock?"

        dossier_lines = [
            f"# 💼 Commercial Sales Intelligence Dossier: {prospect_name}",
            "",
            "> ### 🔒 PRE-ENGAGEMENT CERTIFICATION COMPLETED",
            f"> Certified by `Sales_Intelligence_Node` on `{timestamp}`. Gating released for sales engagement.",
            "",
            "---",
            "",
            "## 1. Executive Prospect Profile & Firmographics",
            f"* **Target Organization:** `{prospect_name}`",
            f"* **Lead Identification Code:** `{lead_id}`",
            f"* **Sector Categorization:** `{industry}`",
            f"* **Annual Revenue Bracket:** `{profile.get('annual_revenue_bracket', 'Unknown')}`",
            f"* **Headcount / Fleet Size:** `{profile.get('employee_count', 'N/A')} active personnel`",
            f"* **Assessed Technical Debt Score:** `{profile.get('estimated_tech_debt_score', 'N/A')} / 100`",
            f"* **Current Software Infrastructure:** `{', '.join(current_stack)}`",
            f"* **Active Operational Bottlenecks:** `{', '.join(bottlenecks) if bottlenecks else 'None Identified'}`",
            "",
            "---",
            "",
            "## 2. Industry Context & Macro Sector Analysis",
            industry_context,
            "",
            "---",
            "",
            "## 3. Mathematical Allocation Matrix & Proofs",
            "The product suite below was determined using the Goings OS Deterministic Allocation Algorithm:",
            "",
            "| Algorithm Factor | Calculated Value | Formulaic Contribution |",
            "| :--- | :--- | :--- |",
            f"| **Revenue Multiplier ($R_m$)** | `{factors['revenue_multiplier']}` | Pricing bracket calibration |",
            f"| **Tech Debt Coefficient ($C_{{td}}$)** | `{factors['tech_debt_coefficient']}` | Automation ROI weighting |",
            f"| **Headcount Scaling ($H_s$)** | `{factors['headcount_scaling']}` | Organizational operational drag |",
            f"| **Bottleneck Impact ($B_i$)** | `{factors['bottleneck_impact']}` | Inefficiency severity multiplier |",
            f"| **Goings OS Suitability Index ($S_{{gos}}$)** | **`{factors['suitability_index']} / 100`** | System readiness & architectural fit |",
            "",
            "$$\\text{Suitability Index } S_{gos} = \\min(100, \\; 30 + 4 R_m + 25 C_{td} + 5 B_i + 3 H_s)$$",
            "",
            "---",
            "",
            "## 4. Precisely Allocated Goings OS Products to Pitch",
            "",
            f"### Pillar 1: Entry Tier -> {entry['tier_name']}",
            f"* **Product Code:** `{entry['tier_code']}`",
            f"* **Initial Implementation Setup:** `${entry['setup_price']:,.2f}`",
            f"* **Monthly Operational Retainer:** `${entry['monthly_retainer']:,.2f}/month`",
            "* **Core Deliverables:**",
            *[f"  - {d}" for d in entry["deliverables"]],
            "",
            f"### Pillar 2: Custom UI -> {ui['ui_name']}",
            f"* **Product Code:** `{ui['ui_code']}`",
            f"* **Component Investment:** `${ui['price']:,.2f} one-time`",
            f"* **Technology Stack:** `{ui['tech_stack']}`",
            "* **Core Deliverables:**",
            *[f"  - {d}" for d in ui["deliverables"]],
            "",
            f"### Pillar 3: Website -> {web['website_name']}",
            f"* **Product Code:** `{web['website_code']}`",
            f"* **Digital Architecture Investment:** `${web['price']:,.2f} one-time`",
            f"* **Underlying Framework:** `{web['architecture']}`",
            "* **Core Deliverables:**",
            *[f"  - {d}" for d in web["deliverables"]],
            "",
            "---",
            "",
            "## 5. Commercial Financial Summary & ROI Forecast",
            "",
            "| Commercial Dimension | Value in USD | Description |",
            "| :--- | :--- | :--- |",
            f"| **Initial Implementation Setup** | **`${fin['initial_implementation_investment']:,.2f}`** | Entry Tier setup + Custom UI + Website |",
            f"| **Annualized Retainer (12 mo)** | **`${fin['annual_maintenance_retainer']:,.2f}`** | Continuous daemon orchestration & vault sync |",
            f"| **Total Year-One Contract Value** | **`${fin['total_year_one_contract_value']:,.2f}`** | Total gross contracted revenue |",
            f"| **Projected Annual Labor Savings** | **`${fin['projected_annual_labor_savings']:,.2f}`** | Elimination of manual re-keying & SaaS debt |",
            f"| **Net Annual Operational ROI** | **`${fin['net_annual_roi_value']:,.2f}`** | Projected net financial gain year one |",
            f"| **Calculated ROI Multiple** | **`+{fin['projected_roi_percentage']}%`** | Return on invested technology capital |",
            f"| **Estimated Amortization Payback** | **`{fin['payback_period_days']} Days`** | Rapid capital payback timeframe |",
            "",
            "---",
            "",
            "## 6. Sales Engagement Battlecard & Tactical Playbook",
            "",
            "### 30-Second Tailored Elevator Pitch",
            f"> \"We noticed {prospect_name} is operating in {industry} while managing legacy systems like {', '.join(current_stack[:2])}. "
            f"Our architecture team built Goings OS specifically to eradicate {', '.join(bottlenecks[:2]) if bottlenecks else 'operational drag'}. "
            f"By deploying the **{entry['tier_name']}**, pairing it with our **{ui['ui_name']}**, and backing it with the "
            f"**{web['website_name']}**, your team captures an estimated **${fin['projected_annual_labor_savings']:,.2f}** in annual labor efficiency "
            f"with a verified payback period of just **{fin['payback_period_days']} days**.\"",
            "",
            "### Primary Discovery Question",
            f"> \"*{discovery_q}*\"",
            "",
            "### Objection Handling Matrix",
            "1. **Objection: 'We already pay for HubSpot and Zapier.'**",
            "   - *Response:* 'HubSpot and Zapier are generic tools that charge exponentially per task while leaking your proprietary data across third-party clouds. Goings OS is your own sovereign operating system: zero per-task charges, sub-millisecond execution, and 100% private vault ownership.'",
            "2. **Objection: 'We prefer to build our internal tools in-house.'**",
            "   - *Response:* 'Building this in-house requires 6-9 months of senior engineering payroll ($180K+). Goings OS provides a battle-tested, pre-architected kernel that deploys in under 14 days for a fraction of internal development burn.'",
            "3. **Objection: 'Can we start small before committing to the full ecosystem?'**",
            f"   - *Response:* 'Precisely. That is why our mathematical algorithm specifically recommends the **{entry['tier_name']}** at ${entry['setup_price']:,.2f} as your foundational milestone.'",
            "",
            "### Closing Sequence",
            "1. Validate the $S_{gos}$ score and firmographic inputs on the discovery call.",
            "2. Dispatch the pre-compiled Presentation Deck generated by `Presentation_Specialist`.",
            f"3. Issue the Master Services Agreement for **${fin['total_year_one_contract_value']:,.2f}** via `Intake_Dispatcher`.",
            "",
            "---",
            f"*Dossier Generated Autonomously by Goings-OS Agent Bus // Node 05 Analyst // {self.AGENT_ID}*"
        ]

        dossier_content = "\n".join(dossier_lines)

        with open(dossier_path, "w", encoding="utf-8") as f:
            f.write(dossier_content)

        with open(telemetry_path, "w", encoding="utf-8") as f:
            json.dump(math_res, f, indent=2)

        self.dossiers_compiled += 1
        self._record_heartbeat()
        logging.info(f"Sales dossier generated successfully: {dossier_path}")

        return {
            "dossier_file": dossier_path,
            "telemetry_file": telemetry_path
        }

    def process_sales_directive(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforces the mandatory directive: generates a dossier and mathematical product suite
        before the sales team engages.
        """
        lead_id = payload.get("lead_id", f"lead_{uuid.uuid4().hex[:8]}")
        prospect_name = payload.get("prospect_name", "Enterprise Prospect")
        industry = payload.get("industry")
        profile = payload.get("company_profile", {})
        acknowledged = payload.get("mandatory_directive_acknowledged", False)

        has_industry = bool(industry)
        has_rev = bool(profile.get("annual_revenue_bracket"))
        has_headcount = bool(profile.get("employee_count"))
        has_debt = "estimated_tech_debt_score" in profile

        missing_fields = []
        if not acknowledged:
            missing_fields.append("mandatory_directive_acknowledged")
        if not has_industry:
            missing_fields.append("industry")
        if not has_rev:
            missing_fields.append("company_profile.annual_revenue_bracket")
        if not has_headcount:
            missing_fields.append("company_profile.employee_count")
        if not has_debt:
            missing_fields.append("company_profile.estimated_tech_debt_score")

        # CHECK MANDATORY DIRECTIVE GATING
        if missing_fields:
            logging.warning(f"MANDATORY DIRECTIVE GATING: Lead '{prospect_name}' missing required fields: {missing_fields}")
            embargo_text = self.build_embargo_notice(lead_id, prospect_name, missing_fields)
            slug = "".join([c if c.isalnum() else "_" for c in prospect_name.lower()]).strip("_")
            embargo_file = os.path.join(self.dossiers_dir, f"embargo_{lead_id}_{slug}.md")

            with open(embargo_file, "w", encoding="utf-8") as f:
                f.write(embargo_text)

            self.embargoes_logged += 1
            self._record_heartbeat()

            return {
                "status": "EMBARGOED_AWAITING_FIRMOGRAPHICS",
                "lead_id": lead_id,
                "prospect_name": prospect_name,
                "message": "Sales engagement is strictly embargoed. Complete required lead firmographics before sales outreach.",
                "embargo_file": embargo_file,
                "missing_fields": missing_fields
            }

        # DIRECTIVE ACKNOWLEDGED & COMPLETE: Calculate mathematical suite & generate dossier
        def _exec_sales_suite(p: Dict[str, Any]) -> Dict[str, Any]:
            logging.info(f"Computing mathematical product allocation for prospect: '{prospect_name}' [{industry}]")
            math_res = self.calculate_mathematical_suite(p)
            artifacts = self.generate_sales_dossier(p, math_res)
            return {
                "status": "DOSSIER_COMPILED_READY_FOR_SALES",
                "lead_id": lead_id,
                "prospect_name": prospect_name,
                "industry": industry,
                "dossier_file": artifacts["dossier_file"],
                "telemetry_file": artifacts["telemetry_file"],
                "suitability_index": math_res["math_factors"]["suitability_index"],
                "total_contract_value": math_res["financial_summary"]["total_year_one_contract_value"],
                "projected_annual_savings": math_res["financial_summary"]["projected_annual_labor_savings"],
                "allocated_products": {
                    "entry_tier": math_res["allocated_products"]["entry_tier"]["tier_name"],
                    "custom_ui": math_res["allocated_products"]["custom_ui"]["ui_name"],
                    "website": math_res["allocated_products"]["website"]["website_name"]
                }
            }

        task_id = f"task_sales_{lead_id}"
        if hasattr(self, "execute_with_god_mode"):
            god_mode_result = self.execute_with_god_mode(
                task_id=task_id,
                action_name="ORCHESTRATE_SALES_INTELLIGENCE",
                payload=payload,
                executor_func=_exec_sales_suite
            )
            return god_mode_result["output"]
        return _exec_sales_suite(payload)

    # Method alias matching the MCP tool schema name
    orchestrate_sales_intelligence = process_sales_directive

    def process_command_queue(self) -> None:
        """Watches queue folder for lead records deposited by Intake_Dispatcher or webhooks."""
        for item in os.listdir(self.queue_dir):
            if item.endswith(".json") and not item.startswith(".") and not item.startswith("completed_") and not item.startswith("error_"):
                job_file = os.path.join(self.queue_dir, item)
                try:
                    with open(job_file, "r", encoding="utf-8") as f:
                        payload = json.load(f)
                    logging.info(f"Processing queued sales intelligence job: {item}")
                    self.process_sales_directive(payload)
                    done_file = os.path.join(self.queue_dir, f"completed_{item}")
                    os.rename(job_file, done_file)
                except Exception as err:
                    logging.error(f"Failed to process sales job {item}: {str(err)}")
                    error_file = os.path.join(self.queue_dir, f"error_{item}")
                    try:
                        os.rename(job_file, error_file)
                    except Exception:
                        pass

    def _record_heartbeat(self) -> None:
        """Writes status and telemetry to persistent status JSON."""
        status_data = {
            "agent_id": self.AGENT_ID,
            "agent_name": self.AGENT_NAME,
            "status": "ACTIVE" if self.running else "STANDBY",
            "mandatory_directive_active": True,
            "uptime_seconds": int(time.time() - self.start_time),
            "dossiers_compiled": self.dossiers_compiled,
            "embargoes_logged": self.embargoes_logged,
            "memorized_tool": "orchestrate_sales_intelligence",
            "required_parameters": self.required_parameters,
            "supported_parameters": list(self.memorized_parameters.keys()),
            "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "dossiers_directory": self.dossiers_dir,
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
        logging.info("Sales_Intelligence_Node daemon loop started. Remaining active in background.")

        def shutdown(signum, frame):
            logging.info("Received shutdown signal. Gracefully exiting...")
            self.running = False

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        while self.running:
            self.process_command_queue()
            self._record_heartbeat()
            time.sleep(2.0)

        logging.info("Sales_Intelligence_Node daemon stopped.")


if __name__ == "__main__":
    daemon = SalesIntelligenceNodeDaemon()
    daemon.run_forever()
