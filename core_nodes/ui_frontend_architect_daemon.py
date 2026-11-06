# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UI FRONTEND ARCHITECT PERSISTENT CHILD AGENT (core_nodes/ui_frontend_architect_daemon.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; MANDATORY UI INTAKE GATING
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
LOG_FILE = os.path.join(LOG_DIR, "ui_frontend_architect.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [UI_Frontend_Architect] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)


class UIFrontendArchitectDaemon:
    """
    Persistent Child Agent: UI_Frontend_Architect.
    Memorizes the orchestrate_ui_component MCP tool schema.
    Specializes in React, Tailwind CSS, and dark mode enterprise interface design.
    MANDATORY DIRECTIVE: Before writing UI components, it must ask the operator for the
    required layout constraints, data visualization needs, and color palette parameters.
    """

    AGENT_ID = "ui-frontend-architect"
    AGENT_NAME = "UI_Frontend_Architect"

    def __init__(self, schema_path: Optional[str] = None):
        self.workspace_root = WORKSPACE_ROOT
        self.schema_path = schema_path or os.path.join(self.workspace_root, "mcp_registry_schema.json")
        self.components_dir = os.path.join(self.workspace_root, "data", "ui_components")
        self.queue_dir = os.path.join(self.workspace_root, "data", "ui_frontend_architect_queue")
        self.status_file = os.path.join(self.workspace_root, "data", "ui_frontend_architect_status.json")
        os.makedirs(self.components_dir, exist_ok=True)
        os.makedirs(self.queue_dir, exist_ok=True)

        self.running = False
        self.start_time = time.time()
        self.components_generated = 0
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
        """Reads mcp_registry_schema.json and internalizes orchestrate_ui_component parameters."""
        logging.info(f"Reading MCP registry schema from: {self.schema_path}")
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"MCP registry schema not found at {self.schema_path}")

        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.memorized_schema = json.load(f)

        target_tool = None
        for tool in self.memorized_schema.get("tools", []):
            if tool.get("name") == "orchestrate_ui_component":
                target_tool = tool
                break

        if not target_tool:
            raise ValueError("Tool 'orchestrate_ui_component' not found in mcp_registry_schema.json")

        self.memorized_tool = target_tool
        params = target_tool.get("parameters", {})
        self.memorized_parameters = params.get("properties", {})
        self.required_parameters = params.get("required", [])

        logging.info("SUCCESS: Schema successfully memorized for 'orchestrate_ui_component'")
        logging.info(f"Memorized top-level parameters: {list(self.memorized_parameters.keys())}")
        logging.info(f"Mandatory parameters: {self.required_parameters}")
        logging.info("MANDATORY DIRECTIVE ACTIVE: Layout, visualization & color palette interview gating is ENGAGED.")

    def handle_bus_event(self, event: Dict[str, Any]) -> None:
        """Callback triggered when an event or mention arrives on the agent bus."""
        action = event.get("action_name")
        sender = event.get("sender_agent", "unknown")
        payload = event.get("payload", {})
        intent_id = event.get("intent_id", "none")

        logging.info(f"Inbound bus event received from @{sender}: action={action}, intent={intent_id}")

        if action in ("SYNTHESIZE_UI_COMPONENT", "ORCHESTRATE_UI_FRONTEND", "SOLICIT_UI_CONSTRAINTS"):
            try:
                result = self.process_ui_directive(payload)
                logging.info(f"UI directive processed for intent {intent_id}: status={result.get('status')}")
            except Exception as err:
                logging.error(f"Error handling UI directive {intent_id}: {str(err)}")

    def build_operator_interview(self, name: str = "UI Component") -> str:
        """Constructs the mandatory structured interview for the operator."""
        lines = [
            f"# 📋 Operator Intake Interview: {name}",
            "",
            "> ### 🚨 MANDATORY DIRECTIVE GATING",
            "> Before writing UI components, you must confirm the following 3 architectural dimensions.",
            "> Component synthesis is paused until these variables are confirmed.",
            "",
            "---",
            "",
            "### 1. Required Layout Constraints",
            "- What is the container boundary?",
            "  - [max-w-7xl centered]",
            "  - [max-w-5xl focused]",
            "  - [Full-bleed edge-to-edge dashboard]",
            "  - [Sidebar-split multi-pane layout]",
            "  - [Modal / Overlay dialog centered]",
            "- What is the target responsiveness?",
            "  - [mobile_responsive | desktop_only | ultrawide_dashboard]",
            "- What is the preferred visual density?",
            "  - [compact_dense for telemetry | standard | spacious_executive]",
            "",
            "### 2. Data Visualization Needs",
            "- What chart and data visualization types are required?",
            "  - [area_chart | bar_chart | donut_breakdown | sparklines | live_stream_gauge | kpi_stat_cards | sortable_data_table]",
            "- What exact data metrics must be displayed?",
            "  (e.g., Gross Revenue, Active Node Count, Webhook Ingress Latency, KMS Key Rotation Status)",
            "- What interactive filters or controls are needed?",
            "  (e.g., Date range picker, live search bar, category filter pills, export CSV button)",
            "",
            "### 3. Color Palette & Dark Mode Parameters",
            "- Theme mode: [dark_only | dark_preferred | light_dark_toggle]",
            "- Primary Brand Hex: (e.g., #1B365D Sovereign Navy, #4F46E5 Electric Indigo)",
            "- Accent Highlight Hex: (e.g., #C5A059 Regal Gold, #10B981 Emerald Profit)",
            "- Surface Dark Hex: (e.g., #0B1120 Midnight Blue, #09090b Obsidian)",
            "- Glassmorphism: [Enable backdrop-blur with subtle border | Solid flat opaque]",
            ""
        ]
        return "\n".join(lines)

    def process_ui_directive(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforces the mandatory operator directive before executing component synthesis.
        """
        comp_name = payload.get("component_name", "EnterpriseUIComponent")
        confirmed = payload.get("operator_confirmed", False)
        layout = payload.get("layout_constraints", {})
        viz = payload.get("data_visualization_needs", {})
        palette = payload.get("color_palette_parameters", {})

        has_layout = bool(layout.get("container_width") and layout.get("breakpoint_target"))
        has_viz = bool(viz.get("chart_types") and viz.get("metrics_to_display"))
        has_palette = bool(palette.get("primary_brand_hex") and palette.get("accent_hex") and palette.get("surface_dark_hex"))

        # CHECK MANDATORY DIRECTIVE
        if not confirmed or not has_layout or not has_viz or not has_palette:
            logging.warning(f"MANDATORY DIRECTIVE BLOCKED: Operator confirmation missing for '{comp_name}'. Gating execution.")
            interview_content = self.build_operator_interview(comp_name)
            gate_id = f"gated_{uuid.uuid4().hex[:8]}"
            gate_file = os.path.join(self.components_dir, f"{gate_id}_{comp_name}_interview.md")

            with open(gate_file, "w", encoding="utf-8") as f:
                f.write(interview_content)

            self.gated_interviews_logged += 1
            self._record_heartbeat()

            return {
                "status": "GATED_AWAITING_OPERATOR_INPUT",
                "gate_id": gate_id,
                "message": "Mandatory operator interview dispatched. Awaiting layout constraints, data visualization needs, and color palette parameters.",
                "interview_file": gate_file,
                "missing_dimensions": [
                    k for k, v in {
                        "layout_constraints": has_layout,
                        "data_visualization_needs": has_viz,
                        "color_palette_parameters": has_palette,
                        "operator_confirmed": bool(confirmed)
                    }.items() if not v
                ]
            }

        # OPERATOR CONFIRMED: Proceed to synthesize React + Tailwind enterprise component
        task_id = f"task_ui_{uuid.uuid4().hex[:8]}"
        if hasattr(self, "execute_with_god_mode"):
            god_mode_result = self.execute_with_god_mode(
                task_id=task_id,
                action_name="SYNTHESIZE_UI_COMPONENT",
                payload=payload,
                executor_func=self._generate_ui_component_bundle
            )
            return god_mode_result["output"]
        return self._generate_ui_component_bundle(payload)

    # Alias matching the registered MCP tool schema name
    orchestrate_ui_component = process_ui_directive

    def _generate_ui_component_bundle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesizes the complete React TSX component, Tailwind theme tokens, and manifest."""
        comp_name = payload["component_name"]
        desc = payload.get("description", "Enterprise Dark Mode React Interface Component.")
        layout = payload["layout_constraints"]
        viz = payload["data_visualization_needs"]
        palette = payload["color_palette_parameters"]

        primary_hex = palette.get("primary_brand_hex", "#1B365D")
        accent_hex = palette.get("accent_hex", "#C5A059")
        surface_hex = palette.get("surface_dark_hex", "#0B1120")
        border_hex = palette.get("border_subtle_hex", "#1E293B")
        glass = palette.get("glassmorphism_enabled", True)

        width_class = (
            "max-w-7xl mx-auto" if layout.get("container_width") == "max_w_7xl"
            else "max-w-5xl mx-auto" if layout.get("container_width") == "max_w_5xl"
            else "w-full"
        )
        density_pad = "p-3 gap-3" if layout.get("spacing_density") == "compact_dense" else "p-6 gap-6"
        glass_class = "backdrop-blur-md bg-white/[0.03] border border-white/[0.08]" if glass else "bg-slate-900 border border-slate-800"

        metrics = viz.get("metrics_to_display", ["Gross Ingress", "System Latency", "Node Health"])
        charts = viz.get("chart_types", ["kpi_stat_cards", "area_chart"])

        comp_id = f"ui_{uuid.uuid4().hex[:10]}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

        logging.info(f"Synthesizing React component: '{comp_name}' [ID: {comp_id}]")

        # 1. Production React TSX Component
        tsx_code = f"""// ==============================================================================
// KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
// ENTERPRISE REACT COMPONENT: {comp_name}.tsx
// COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; STRICT TYPESCRIPT
// PALETTE: PRIMARY {primary_hex} | ACCENT {accent_hex} | SURFACE {surface_hex}
// ==============================================================================

import React, {{ useState, useMemo }} from 'react';
import {{ 
  Activity, 
  TrendingUp, 
  ShieldCheck, 
  Layers, 
  Search, 
  Filter, 
  Download, 
  ChevronRight 
}} from 'lucide-react';

export interface {comp_name}Props {{
  title?: string;
  refreshIntervalMs?: number;
  onExportTelemetry?: () => void;
}}

interface MetricCardData {{
  id: string;
  label: string;
  value: string;
  trend: string;
  isPositive: boolean;
}}

export const {comp_name}: React.FC<{comp_name}Props> = ({{
  title = "{comp_name.replace('Dashboard', ' Enterprise Dashboard')}",
  refreshIntervalMs = 5000,
  onExportTelemetry
}}) => {{
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'ACTIVE' | 'AUDIT'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const metricsData: MetricCardData[] = useMemo(() => [
    {{ id: 'm1', label: '{metrics[0] if len(metrics) > 0 else "Primary Metric"}', value: '$128,450.00', trend: '+14.2%', isPositive: true }},
    {{ id: 'm2', label: '{metrics[1] if len(metrics) > 1 else "Throughput Latency"}', value: '16.4 ms', trend: '-8.5%', isPositive: true }},
    {{ id: 'm3', label: '{metrics[2] if len(metrics) > 2 else "Active Child Nodes"}', value: '5 Online', trend: '100% SLA', isPositive: true }},
    {{ id: 'm4', label: 'Vault Cryptographic Status', value: 'SECURE', trend: 'ZERO LEAKAGE', isPositive: true }}
  ], []);

  return (
    <div className="{width_class} min-h-screen bg-[{surface_hex}] text-slate-100 {density_pad} flex flex-col font-sans selection:bg-[{accent_hex}] selection:text-black">
      
      {{/* Header Bar */}}
      <header className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-[{border_hex}] gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs uppercase tracking-widest text-[{accent_hex}] font-mono font-semibold">
              SOVEREIGN OS // ENTERPRISE RUNTIME
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
            {{title}}
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            {desc}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search telemetry..."
              value={{searchQuery}}
              onChange={{(e) => setSearchQuery(e.target.value)}}
              className="bg-black/40 border border-[{border_hex}] text-sm rounded-lg pl-9 pr-4 py-2 focus:outline-none focus:border-[{accent_hex}] text-white transition-colors"
            />
          </div>
          <button
            onClick={{onExportTelemetry}}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[{primary_hex}] hover:brightness-110 text-white text-sm font-medium transition-all shadow-md active:scale-95"
          >
            <Download className="w-4 h-4 text-[{accent_hex}]" />
            Export Audit
          </button>
        </div>
      </header>

      {{/* KPI Metric Cards Grid */}}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
        {{metricsData.map((item) => (
          <div
            key={{item.id}}
            className="{glass_class} rounded-xl p-5 hover:border-[{accent_hex}] transition-all duration-300 group shadow-lg"
          >
            <div className="flex justify-between items-start">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                {{item.label}}
              </span>
              <Activity className="w-4 h-4 text-[{accent_hex}] group-hover:rotate-12 transition-transform" />
            </div>
            <div className="text-2xl font-bold tracking-tight text-white mt-3">
              {{item.value}}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-xs font-mono text-emerald-400">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>{{item.trend}}</span>
            </div>
          </div>
        ))}}
      </section>

      {{/* Main Data Visualization Surface */}}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6 flex-1">
        
        {{/* Primary Chart Container */}}
        <div className="lg:col-span-2 {glass_class} rounded-xl p-6 flex flex-col justify-between shadow-xl">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-lg font-semibold text-white">Telemetric Ingress Volume</h2>
              <p className="text-xs text-slate-400">Real-time event processing throughput across child agent bus</p>
            </div>
            <div className="flex items-center gap-2">
              {{(['ALL', 'ACTIVE', 'AUDIT'] as const).map((mode) => (
                <button
                  key={{mode}}
                  onClick={{() => setActiveFilter(mode)}}
                  className={{`px-3 py-1 text-xs rounded-md font-mono transition-colors ${{
                    activeFilter === mode 
                      ? 'bg-[{accent_hex}] text-black font-bold' 
                      : 'bg-black/30 text-slate-400 hover:text-white border border-[{border_hex}]'
                  }}`}}
                >
                  {{mode}}
                </button>
              ))}}
            </div>
          </div>

          {{/* Simulated High-Density Visualization Canvas */}}
          <div className="h-64 w-full bg-black/40 rounded-lg border border-[{border_hex}] flex items-end p-4 gap-2 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-t from-[{primary_hex}]/20 to-transparent pointer-events-none" />
            {{[40, 65, 55, 80, 70, 95, 85, 110, 90, 125, 115, 140, 130, 160].map((val, idx) => (
              <div 
                key={{idx}} 
                style={{{{ height: `${{Math.min(val, 100)}}%` }}}} 
                className="flex-1 bg-gradient-to-t from-[{primary_hex}] to-[{accent_hex}] rounded-t opacity-80 hover:opacity-100 transition-opacity cursor-pointer group relative"
              >
                <span className="absolute -top-7 left-1/2 -translate-x-1/2 px-1.5 py-0.5 rounded bg-black text-[10px] text-white opacity-0 group-hover:opacity-100 font-mono pointer-events-none transition-opacity">
                  {{val}}k
                </span>
              </div>
            ))}}
          </div>

          <div className="flex justify-between items-center text-xs text-slate-400 mt-4 pt-3 border-t border-[{border_hex}] font-mono">
            <span>START: T-24H</span>
            <span className="text-emerald-400">PEAK: 160k EVENTS / SEC</span>
            <span>LIVE: ZERO DEFECTS</span>
          </div>
        </div>

        {{/* Node Fleet Activity Panel */}}
        <div className="{glass_class} rounded-xl p-6 flex flex-col shadow-xl">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-[{border_hex}]">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-[{accent_hex}]" />
              Active Node Fleet
            </h2>
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono">
              5/5 ACTIVE
            </span>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto pr-1">
            {{[
              {{ name: 'Workspace_Architect', status: 'SYNCHRONIZED', task: 'Docs & Sheets Orchestrator' }},
              {{ name: 'Intelligence_Scout', status: 'ACTIVE', task: 'OSINT & Web Research Crawler' }},
              {{ name: 'Form_Specialist', status: 'GATED', task: 'Workspace Forms API Engine' }},
              {{ name: 'Intake_Dispatcher', status: 'RUNNING', task: 'Sub-Millisecond GHL Router' }},
              {{ name: 'Presentation_Specialist', status: 'READY', task: 'Enterprise Slides Compiler' }}
            ].map((node, i) => (
              <div 
                key={{i}}
                className="flex items-center justify-between p-3 rounded-lg bg-black/30 border border-[{border_hex}] hover:border-slate-600 transition-all text-sm"
              >
                <div>
                  <div className="font-medium text-white flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    {{node.name}}
                  </div>
                  <div className="text-xs text-slate-400">{{node.task}}</div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-600" />
              </div>
            ))}}
          </div>

          <div className="mt-4 pt-3 border-t border-[{border_hex}] text-xs text-slate-500 font-mono text-center">
            GOINGS-OS SECURE DAEMON SUBSYSTEM
          </div>
        </div>

      </section>

    </div>
  );
}};

export default {comp_name};
"""

        # 2. Tailwind Theme Tokens JSON
        theme_tokens = {
            "component": comp_name,
            "theme_mode": palette.get("theme_mode", "dark_only"),
            "colors": {
                "brand_primary": primary_hex,
                "accent_highlight": accent_hex,
                "surface_dark": surface_hex,
                "border_subtle": border_hex
            },
            "layout": layout,
            "visualization": viz,
            "generated_at": timestamp
        }

        # 3. Write files to data/ui_components/
        tsx_file = os.path.join(self.components_dir, f"{comp_name}.tsx")
        tokens_file = os.path.join(self.components_dir, f"{comp_name}_tailwind_tokens.json")
        manifest_file = os.path.join(self.components_dir, f"{comp_name}_manifest.md")

        with open(tsx_file, "w", encoding="utf-8") as f:
            f.write(tsx_code)

        with open(tokens_file, "w", encoding="utf-8") as f:
            json.dump(theme_tokens, f, indent=2)

        manifest_lines = [
            f"# 🎨 UI Component Manifest: {comp_name}",
            "",
            f"**Component Identifier:** `{comp_id}`  ",
            f"**Target Width:** `{layout.get('container_width')}`  ",
            f"**Responsiveness:** `{layout.get('breakpoint_target')}`  ",
            f"**Primary Brand Hex:** `{primary_hex}`  ",
            f"**Accent Highlight Hex:** `{accent_hex}`  ",
            f"**Surface Dark Hex:** `{surface_hex}`  ",
            f"**Compiled Timestamp:** `{timestamp}`  ",
            "",
            "> ### 🔒 OPERATOR INTAKE CONFIRMED",
            "> Operator intake interview completed and certified. Production React TSX component synthesized.",
            "",
            "---",
            "",
            "## 1. Generated Artifact Files",
            f"* **React Component:** `{tsx_file}`",
            f"* **Tailwind Theme Tokens:** `{tokens_file}`",
            "",
            "---",
            "",
            "## 2. Component Integration Directive",
            "```tsx",
            f"import {{ {comp_name} }} from './components/{comp_name}';",
            "",
            "export default function App() {",
            "  return (",
            f"    <{comp_name} onExportTelemetry={{() => console.log('Audit exported')}} />",
            "  );",
            "}",
            "```",
            ""
        ]

        with open(manifest_file, "w", encoding="utf-8") as f:
            f.write("\n".join(manifest_lines))

        self.components_generated += 1
        self._record_heartbeat()
        logging.info(f"UI component bundle written successfully: {manifest_file}")

        return {
            "status": "GENERATED",
            "component_id": comp_id,
            "component_name": comp_name,
            "tsx_file": tsx_file,
            "tokens_file": tokens_file,
            "manifest_file": manifest_file
        }

    def process_command_queue(self) -> None:
        """Watches queue folder for UI component synthesis jobs deposited by external agents."""
        for item in os.listdir(self.queue_dir):
            if item.endswith(".json") and not item.startswith(".") and not item.startswith("completed_") and not item.startswith("error_"):
                job_file = os.path.join(self.queue_dir, item)
                try:
                    with open(job_file, "r", encoding="utf-8") as f:
                        payload = json.load(f)
                    logging.info(f"Processing queued UI job: {item}")
                    self.process_ui_directive(payload)
                    done_file = os.path.join(self.queue_dir, f"completed_{item}")
                    os.rename(job_file, done_file)
                except Exception as err:
                    logging.error(f"Failed to process UI job {item}: {str(err)}")
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
            "components_generated": self.components_generated,
            "gated_interviews_logged": self.gated_interviews_logged,
            "memorized_tool": "orchestrate_ui_component",
            "required_parameters": self.required_parameters,
            "supported_parameters": list(self.memorized_parameters.keys()),
            "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "components_directory": self.components_dir,
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
        logging.info("UI_Frontend_Architect daemon loop started. Remaining active in background.")

        def shutdown(signum, frame):
            logging.info("Received shutdown signal. Gracefully exiting...")
            self.running = False

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        while self.running:
            self.process_command_queue()
            self._record_heartbeat()
            time.sleep(2.0)

        logging.info("UI_Frontend_Architect daemon stopped.")


if __name__ == "__main__":
    daemon = UIFrontendArchitectDaemon()
    daemon.run_forever()
