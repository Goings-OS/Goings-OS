# KEPT IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: GOHIGHLEVEL INBOUND WEBHOOK INTERCEPTOR (PRODUCTION)
import os
import sys

try:
    from flask import Flask, request, jsonify
except ImportError:
    os.system("pip install flask")
    from flask import Flask, request, jsonify

from waitress import serve

sys.path.append(r"C:\Google\CloudSDK\Goings-OS\core_nodes\node_08_vault")
try:
    from tenant_storage import provision_new_client_sandbox
except ImportError:
    provision_new_client_sandbox = None

app = Flask(__name__)

@app.route("/webhook/ghl_onboarding", methods=["POST"])
def handle_ghl_onboarding_payload():
    payload = request.get_json()
    if not payload:
        return jsonify({"status": "REJECTED", "message": "Missing payload data structures"}), 400
        
    tenant_id = payload.get("tenant_id")
    business_name = payload.get("business_name")
    email = payload.get("email")
    api_key = payload.get("api_key")
    tier = payload.get("subscription_tier", "Standard Base Core Platform")
    
    if not all([tenant_id, business_name, email, api_key]):
        return jsonify({"status": "INCOMPLETE", "message": "Required validation fields missing"}), 400
        
    print(f"[PRODUCTION INGRESS] Processing entry packet for: {business_name}")
    
    if provision_new_client_sandbox:
        try:
            provision_new_client_sandbox(tenant_id=tenant_id, business_name=business_name, email=email, api_key=api_key, tier=tier)
            return jsonify({"status": "SUCCESS", "message": f"Private sandbox environment initialized for {business_name}"}), 200
        except Exception as system_fault:
            return jsonify({"status": "SERVER_ERROR", "message": str(system_fault)}), 500
    else:
        return jsonify({"status": "DEGRADED", "message": "Vault core database offline"}), 500

if __name__ == "__main__":
    print("[PRODUCTION READY] Goings-OS Inbound Webhook Service running via Waitress WSGI.")
    print("Listening for secure data streams on port 5000...")
    serve(app, host="0.0.0.0", port=5000)
