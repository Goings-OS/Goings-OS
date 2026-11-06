# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: FORM SPECIALIST PERSISTENT CHILD AGENT (core_nodes/form_specialist_daemon.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; MANDATORY OPERATOR INTAKE GATING
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
LOG_FILE = os.path.join(LOG_DIR, "form_specialist.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Form_Specialist] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)


class FormSpecialistDaemon:
    """
    Persistent Child Agent: Form_Specialist.
    Memorizes the orchestrate_google_form MCP tool schema and manages Google Workspace
    Forms generation. Enforces mandatory operator intake gating prior to form creation.
    """

    AGENT_ID = "form-specialist"
    AGENT_NAME = "Form_Specialist"

    def __init__(self, schema_path: Optional[str] = None):
        self.workspace_root = WORKSPACE_ROOT
        self.schema_path = schema_path or os.path.join(self.workspace_root, "mcp_registry_schema.json")
        self.forms_dir = os.path.join(self.workspace_root, "data", "forms")
        self.queue_dir = os.path.join(self.workspace_root, "data", "form_specialist_queue")
        self.status_file = os.path.join(self.workspace_root, "data", "form_specialist_status.json")
        os.makedirs(self.forms_dir, exist_ok=True)
        os.makedirs(self.queue_dir, exist_ok=True)

        self.running = False
        self.start_time = time.time()
        self.forms_generated = 0
        self.gated_intakes_logged = 0
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
        """Reads mcp_registry_schema.json and internalizes orchestrate_google_form parameters."""
        logging.info(f"Reading MCP registry schema from: {self.schema_path}")
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"MCP registry schema not found at {self.schema_path}")

        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.memorized_schema = json.load(f)

        target_tool = None
        for tool in self.memorized_schema.get("tools", []):
            if tool.get("name") == "orchestrate_google_form":
                target_tool = tool
                break

        if not target_tool:
            raise ValueError("Tool 'orchestrate_google_form' not found in mcp_registry_schema.json")

        self.memorized_tool = target_tool
        params = target_tool.get("parameters", {})
        self.memorized_parameters = params.get("properties", {})
        self.required_parameters = params.get("required", [])

        logging.info("SUCCESS: Schema successfully memorized for 'orchestrate_google_form'")
        logging.info(f"Memorized top-level parameters: {list(self.memorized_parameters.keys())}")
        logging.info(f"Mandatory parameters: {self.required_parameters}")
        logging.info("MANDATORY DIRECTIVE ACTIVE: Operator intake questionnaire enforcement is ENGAGED.")

    def handle_bus_event(self, event: Dict[str, Any]) -> None:
        """Callback triggered when an event or mention arrives on the agent bus."""
        action = event.get("action_name")
        sender = event.get("sender_agent", "unknown")
        payload = event.get("payload", {})
        intent_id = event.get("intent_id", "none")

        logging.info(f"Inbound bus event received from @{sender}: action={action}, intent={intent_id}")

        if action in ("ORCHESTRATE_GOOGLE_FORM", "GENERATE_GOOGLE_FORM", "SOLICIT_OPERATOR_INTAKE"):
            try:
                result = self.process_form_directive(payload)
                logging.info(f"Form directive processed for intent {intent_id}: status={result.get('status')}")
            except Exception as err:
                logging.error(f"Error handling form directive {intent_id}: {str(err)}")

    def build_operator_questionnaire(self, title: str = "Google Form Intake") -> str:
        """Constructs the mandatory structured questionnaire for the operator."""
        lines = [
            f"# 📋 Operator Intake Questionnaire: {title}",
            "",
            "> ### 🚨 MANDATORY DIRECTIVE GATING",
            "> Before executing Google Form creation, you must answer the following 3 structured dimensions.",
            "> Form generation is paused until these parameters are confirmed.",
            "",
            "---",
            "",
            "### Dimension 1: Exact Form Fields & Geometry",
            "1. What is the official Form Title and introductory description?",
            "2. What are the exact fields/questions required? For each field, specify:",
            "   - Field Prompt / Label",
            "   - Field Type: [short_answer | paragraph | multiple_choice | checkboxes | dropdown | linear_scale | date | time]",
            "   - Required status: [Yes | No]",
            "   - Options / Choices (if multiple choice, checkboxes, or dropdown)",
            "   - Helper / guidance text (if applicable)",
            "",
            "### Dimension 2: Target Audience & Context",
            "3. Who is the target audience for this form?",
            "   - [Internal Team / Staff]",
            "   - [High-Ticket Private Clients]",
            "   - [Public Marketing Leads]",
            "   - [Vendor / Contractor Intake]",
            "   - [Compliance / Regulatory Audit]",
            "4. Does this form require login / email collection, or is it anonymous?",
            "",
            "### Dimension 3: Webhook Routing & Ingress Destination",
            "5. What is the target webhook destination URL to receive form submissions?",
            "   (e.g., https://goings-os.internal/api/v1/ingress/forms or external CRM endpoint)",
            "6. What routing engine will process the submission?",
            "   - [Google Apps Script installable onFormSubmit trigger]",
            "   - [Direct HTTP Webhook]",
            "   - [Pub/Sub Cloud Event Bridge]",
            "7. What payload format is required?",
            "   - [json_nested | json_flattened | form_encoded]",
            "8. Is an Authorization Bearer token or HMAC header required?",
            ""
        ]
        return "\n".join(lines)

    def process_form_directive(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforces the mandatory operator directive before executing form creation.
        """
        title = payload.get("title", "Untitled Google Form")
        confirmed = payload.get("operator_confirmed", False)
        fields = payload.get("fields", [])
        audience = payload.get("target_audience")
        webhook = payload.get("webhook_routing")

        # CHECK MANDATORY DIRECTIVE
        if not confirmed or not fields or not audience or not webhook:
            logging.warning(f"MANDATORY DIRECTIVE BLOCKED: Operator confirmation missing for '{title}'. Gating execution.")
            questionnaire_content = self.build_operator_questionnaire(title)
            gate_id = f"gated_{uuid.uuid4().hex[:8]}"
            gate_file = os.path.join(self.forms_dir, f"{gate_id}_{title.replace(' ', '_')}_questionnaire.md")

            with open(gate_file, "w", encoding="utf-8") as f:
                f.write(questionnaire_content)

            self.gated_intakes_logged += 1
            self._record_heartbeat()

            return {
                "status": "GATED_AWAITING_OPERATOR_INPUT",
                "gate_id": gate_id,
                "message": "Mandatory operator intake questionnaire dispatched. Awaiting operator answers before generation.",
                "questionnaire_file": gate_file,
                "missing_dimensions": [
                    k for k, v in {
                        "fields": bool(fields),
                        "target_audience": bool(audience),
                        "webhook_routing": bool(webhook),
                        "operator_confirmed": bool(confirmed)
                    }.items() if not v
                ]
            }

        # OPERATOR CONFIRMED: Proceed to synthesize Google Form assets
        task_id = f"task_form_{uuid.uuid4().hex[:8]}"
        if hasattr(self, "execute_with_god_mode"):
            god_mode_result = self.execute_with_god_mode(
                task_id=task_id,
                action_name="ORCHESTRATE_GOOGLE_FORM",
                payload=payload,
                executor_func=self._generate_google_form_bundle
            )
            return god_mode_result["output"]
        return self._generate_google_form_bundle(payload)

    def _generate_google_form_bundle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesizes the complete Google Forms API spec, Apps Script webhook, and manifest."""
        title = payload["title"]
        audience = payload["target_audience"]
        fields = payload["fields"]
        webhook = payload["webhook_routing"]
        description = payload.get("description", f"Google Form orchestrated for {audience}.")
        form_id = f"form_{uuid.uuid4().hex[:10]}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

        logging.info(f"Synthesizing Google Form Workspace bundle: '{title}' [ID: {form_id}]")

        # 1. Google Forms API v1 batchUpdate payload construction
        batch_items = []
        for idx, fld in enumerate(fields):
            name = fld.get("field_name", f"Question {idx + 1}")
            f_type = fld.get("field_type", "short_answer")
            req = fld.get("required", True)
            opts = fld.get("options", [])
            help_txt = fld.get("help_text", "")

            item: Dict[str, Any] = {
                "title": name,
                "description": help_txt
            }

            if f_type in ("short_answer", "paragraph"):
                item["questionItem"] = {
                    "question": {
                        "required": req,
                        "textQuestion": {
                            "paragraph": (f_type == "paragraph")
                        }
                    }
                }
            elif f_type in ("multiple_choice", "checkboxes", "dropdown"):
                choice_type = "CHECKBOX" if f_type == "checkboxes" else "DROP_DOWN" if f_type == "dropdown" else "RADIO"
                item["questionItem"] = {
                    "question": {
                        "required": req,
                        "choiceQuestion": {
                            "type": choice_type,
                            "options": [{"value": o} for o in (opts or ["Option 1"])]
                        }
                    }
                }
            elif f_type == "linear_scale":
                item["questionItem"] = {
                    "question": {
                        "required": req,
                        "scaleQuestion": {
                            "low": 1,
                            "high": 5,
                            "lowLabel": "Low",
                            "highLabel": "High"
                        }
                    }
                }
            elif f_type == "date":
                item["questionItem"] = {
                    "question": {
                        "required": req,
                        "dateQuestion": {
                            "includeYear": True,
                            "includeTime": False
                        }
                    }
                }

            batch_items.append({
                "createItem": {
                    "item": item,
                    "location": {
                        "index": idx
                    }
                }
            })

        forms_api_spec = {
            "createForm": {
                "info": {
                    "title": title,
                    "documentTitle": f"[Goings-OS] {title}"
                }
            },
            "batchUpdate": {
                "requests": batch_items
            }
        }

        # 2. Automated Google Apps Script Webhook Trigger Script
        dest_url = webhook.get("destination_url")
        auth_token = webhook.get("auth_header_token", "")
        payload_format = webhook.get("payload_format", "json_nested")

        apps_script_code = f"""// ==============================================================================
// KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
// GOOGLE FORMS SUBMISSION WEBHOOK ROUTER (Apps Script Trigger)
// FORM: {title} | AUDIENCE: {audience} | GENERATED: {timestamp}
// ==============================================================================

function onFormSubmit(e) {{
  var formResponse = e.response;
  var itemResponses = formResponse.getItemResponses();
  var payload = {{
    formId: FormApp.getActiveForm().getId(),
    formTitle: "{title}",
    responseId: formResponse.getId(),
    timestamp: formResponse.getTimestamp().toISOString(),
    respondentEmail: formResponse.getRespondentEmail() || "anonymous",
    targetAudience: "{audience}",
    answers: {{}}
  }};

  for (var i = 0; i < itemResponses.length; i++) {{
    var item = itemResponses[i];
    payload.answers[item.getItem().getTitle()] = item.getResponse();
  }}

  var options = {{
    method: "post",
    contentType: "application/json",
    headers: {{
      "Authorization": "{auth_token}",
      "X-Goings-OS-Source": "Form_Specialist",
      "X-Payload-Format": "{payload_format}"
    }},
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  }};

  try {{
    var resp = UrlFetchApp.fetch("{dest_url}", options);
    Logger.log("Webhook dispatched: Status " + resp.getResponseCode());
  }} catch (err) {{
    Logger.log("Webhook dispatch error: " + err.toString());
  }}
}}
"""

        # 3. Write files to data/forms/
        clean_name = title.replace(" ", "_")
        spec_path = os.path.join(self.forms_dir, f"{form_id}_{clean_name}_api_spec.json")
        script_path = os.path.join(self.forms_dir, f"{form_id}_{clean_name}_webhook.js")
        manifest_path = os.path.join(self.forms_dir, f"{form_id}_{clean_name}_manifest.md")

        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump(forms_api_spec, f, indent=2)

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(apps_script_code)

        manifest_lines = [
            f"# 📝 Google Form Manifest: {title}",
            "",
            f"**Form Identifier:** `{form_id}`  ",
            f"**Target Audience:** `{audience}`  ",
            f"**Total Field Count:** `{len(fields)}`  ",
            f"**Webhook Destination:** `{dest_url}`  ",
            f"**Generated Timestamp:** `{timestamp}`  ",
            "",
            "> ### 🔒 OPERATOR CONFIRMATION VERIFIED",
            "> Operator intake questionnaire completed and certified. Form specification generated.",
            "",
            "---",
            "",
            "## 1. Google Forms Field Geometry",
            "",
            "| Index | Question Prompt | Question Type | Required | Options Count |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]

        for idx, fld in enumerate(fields):
            opt_cnt = len(fld.get("options", []))
            manifest_lines.append(f"| {idx + 1} | {fld.get('field_name')} | `{fld.get('field_type')}` | {fld.get('required', True)} | {opt_cnt} |")

        manifest_lines.extend([
            "",
            "---",
            "",
            "## 2. Webhook Routing Specification",
            f"* **Target Endpoint:** `{dest_url}`",
            f"* **Routing Engine:** `{webhook.get('routing_engine', 'apps_script_trigger')}`",
            f"* **Payload Format:** `{payload_format}`",
            f"* **Embedded Apps Script File:** `{script_path}`",
            "",
            "---",
            "",
            "## 3. Google Workspace API Deployment Directive",
            "```bash",
            f"# POST payload to Forms API v1",
            f"curl -X POST https://forms.googleapis.com/v1/forms \\",
            f"  -H 'Authorization: Bearer $(gcloud auth print-access-token)' \\",
            f"  -H 'Content-Type: application/json' \\",
            f"  -d @{spec_path}",
            "```",
            ""
        ])

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write("\n".join(manifest_lines))

        self.forms_generated += 1
        self._record_heartbeat()
        logging.info(f"Form bundle written successfully: {manifest_path}")

        return {
            "status": "GENERATED",
            "form_id": form_id,
            "title": title,
            "api_spec_file": spec_path,
            "webhook_script_file": script_path,
            "manifest_file": manifest_path
        }

    def process_command_queue(self) -> None:
        """Watches queue folder for form creation jobs deposited by external agents."""
        for item in os.listdir(self.queue_dir):
            if item.endswith(".json") and not item.startswith(".") and not item.startswith("completed_") and not item.startswith("error_"):
                job_file = os.path.join(self.queue_dir, item)
                try:
                    with open(job_file, "r", encoding="utf-8") as f:
                        payload = json.load(f)
                    logging.info(f"Processing queued form job: {item}")
                    self.process_form_directive(payload)
                    done_file = os.path.join(self.queue_dir, f"completed_{item}")
                    os.rename(job_file, done_file)
                except Exception as err:
                    logging.error(f"Failed to process form job {item}: {str(err)}")
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
            "forms_generated": self.forms_generated,
            "gated_intakes_logged": self.gated_intakes_logged,
            "memorized_tool": "orchestrate_google_form",
            "required_parameters": self.required_parameters,
            "supported_parameters": list(self.memorized_parameters.keys()),
            "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "forms_directory": self.forms_dir,
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
        logging.info("Form_Specialist daemon loop started. Remaining active in background.")

        def shutdown(signum, frame):
            logging.info("Received shutdown signal. Gracefully exiting...")
            self.running = False

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        while self.running:
            self.process_command_queue()
            self._record_heartbeat()
            time.sleep(2.0)

        logging.info("Form_Specialist daemon stopped.")


if __name__ == "__main__":
    daemon = FormSpecialistDaemon()
    daemon.run_forever()
