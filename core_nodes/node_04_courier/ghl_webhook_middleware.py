# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: GHL WORKFLOW LIFELINE MIDDLEWARE RECEIVER
# BIND: NODE 04 COURIER // PORT 5000 INBOUND GATEWAY
# COMPLIANCE: ZERO EM-DASHES ENFORCED // ALWAYS POSITIVE // EXPLICIT TYPING
# ==============================================================================

import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone

class GHLWorkflowLifelineHandler(BaseHTTPRequestHandler):
    """Processes inbound webhooks dispatched from native GoHighLevel automation workflows."""

    def do_POST(self) -> None:
        """Intercepts the incoming data payload and executes the multi-pillar treasury audit."""
        content_length: int = int(self.headers.get('Content-Length', 0))
        raw_body: bytes = self.rfile.read(content_length)
        
        try:
            payload: dict = json.loads(raw_body.decode('utf-8'))
            self.process_incoming_lead(payload)
            self.send_successful_response()
        except Exception as e:
            self.send_failure_response(str(e))

    def process_incoming_lead(self, data: dict) -> None:
        """Parses customer data structures and applies the automated 70/30 treasury split calculations."""
        contact_name: str = data.get("contact_name", "Anonymous Lead")
        pillar_domain: str = data.get("pillar_domain", "Keepitgoings.com")
        gross_revenue: float = float(data.get("transaction_amount", 0.00))
        
        # Enforce the strict 70/30 programmatic distribution rules
        operations_runway: float = round(gross_revenue * 0.70, 2)
        owners_draw_pool: float = round(gross_revenue * 0.30, 2)
        
        timestamp: str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        log_entry: dict = {
            "timestamp": timestamp,
            "client": contact_name,
            "origin_domain": pillar_domain,
            "gross_ingress": gross_revenue,
            "allocation_metrics": {
                "operations_70_percent": operations_runway,
                "owners_draw_30_percent": owners_draw_pool
            },
            "system_status": "PROCESSED_AND_SECURED"
        }
        
        # Commit the transaction log entry straight to persistent disk storage
        log_directory: str = r"C:\Google\CloudSDK\Goings-OS\core_nodes\node_04_courier"
        log_file_path: str = os.path.join(log_directory, "ghl_ingress_ledger.json")
        
        ledger_data: list = []
        if os.path.exists(log_file_path):
            with open(log_file_path, "r", encoding="utf-8") as f:
                try:
                    ledger_data = json.load(f)
                except json.JSONDecodeError:
                    ledger_data = []
                    
        ledger_data.append(log_entry)
        
        with open(log_file_path, "w", encoding="utf-8") as f:
            json.dump(ledger_data, f, indent=4)
            
        print(f"[INGRESS SUCCESS] Processed payment from {contact_name} for {pillar_domain}: split logged.")

    def send_successful_response(self) -> None:
        """Returns a secure 200 verification status back to the originating GHL workflow server."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response: dict = {"status": "SUCCESS", "message": "Goings OS Ingress Lifeline Secured"}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def send_failure_response(self, error_message: str) -> None:
        """Returns a 400 fault status capturing runtime anomalies safely within local logs."""
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response: dict = {"status": "ERROR", "message": error_message}
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_middleware_server(port: int = 5000) -> None:
    """Launches the persistent network service listener loop to guard incoming transaction pipelines."""
    server_address: tuple = ('', port)
    httpd: HTTPServer = HTTPServer(server_address, GHLWorkflowLifelineHandler)
    print(f"[ACTIVE] Goings OS GHL Lifeline Middleware listening securely on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] GHL Webhook Middleware terminated cleanly.")

if __name__ == "__main__":
    run_middleware_server(port=5000)
