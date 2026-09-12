# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: MODEL CONTEXT PROTOCOL (MCP) MASTER SERVER CONNECTOR
# BIND: NODE 13 DEVELOPER ENGINE // INTEGRATED DATA GATEWAY
# COMPLIANCE: ZERO EM-DASHES ENFORCED // ALWAYS POSITIVE // FULL AUTOMATION
# ==============================================================================

import sys
import json
import os
from datetime import datetime, timezone

class GoingsOsMcpServer:
    """Implements an authoritative Model Context Protocol gateway using JSON-RPC stdio transport."""

    def __init__(self):
        self.vault_dir = r"C:\Google\CloudSDK\Goings-OS\notebook_sources"
        self.sentry_dir = r"C:\Google\CloudSDK\Goings-OS\core_nodes\node_03_sentry"
        self.running = True

    def log_diagnostic(self, message: str):
        """Writes internal runtime tracking logs safely to stderr stream fields."""
        sys.stderr.write(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [MCP_SERVER] {message}\n")
        sys.stderr.flush()

    def list_available_tools(self) -> dict:
        """Exposes authorized system tools to the connecting artificial intelligence model client."""
        return {
            "tools": [
                {
                    "name": "list_notebook_sources",
                    "description": "Lists all available markdown notebook source documents stored in the private corporate vault folder layout.",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "read_notebook_document",
                    "description": "Reads the precise plaintext contents of a specific localized markdown repository asset.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_name": {"type": "string", "description": "The exact target name of the markdown file including extension."}
                        },
                        "required": ["file_name"]
                    }
                },
                {
                    "name": "execute_apollo_compliance_audit",
                    "description": "Invokes Apollo v3.0 to parse target file contents against SOC 2, UCC, US Code, and global AI governance parameters.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_name": {"type": "string", "description": "Target tracking name."},
                            "code_stream": {"type": "string", "description": "Raw code stream string to execute compliance analysis loop on."}
                        },
                        "required": ["file_name", "code_stream"]
                    }
                }
            ]
        }

    def dispatch_tool_execution(self, tool_name: str, arguments: dict) -> dict:
        """Routes the incoming client execution parameters to the requested server action handler."""
        self.log_diagnostic(f"Executing tool action pipeline for: {tool_name}")
        
        if tool_name == "list_notebook_sources":
            if not os.path.exists(self.vault_dir):
                return {"content": [{"type": "text", "text": "Error: Local vault source folder layout missing."}]}
            files = [f for f in os.listdir(self.vault_dir) if f.endswith(".md")]
            return {"content": [{"type": "text", "text": json.dumps({"status": "SUCCESS", "vault_files": files}, indent=2)}]}

        elif tool_name == "read_notebook_document":
            target_file = arguments.get("file_name", "")
            safe_path = os.path.join(self.vault_dir, target_file)
            if not os.path.exists(safe_path) or not target_file.endswith(".md"):
                return {"content": [{"type": "text", "text": f"Error: Target file reference '{target_file}' is invalid or unauthorized."}]}
            with open(safe_path, "r", encoding="utf-8") as f:
                return {"content": [{"type": "text", "text": f.read()}]}

        elif tool_name == "execute_apollo_compliance_audit":
            # Direct module binding invocation mapping across localized engine tracks
            try:
                sys.path.append(self.sentry_dir)
                from apollo_reviewer import ApolloOmniComplianceEngine  # type: ignore
                engine = ApolloOmniComplianceEngine()
                report = engine.execute_compliance_audit(arguments.get("file_name", "mcp_ingress.py"), arguments.get("code_stream", ""))
                return {"content": [{"type": "text", "text": json.dumps(report, indent=2)}]}
            except Exception as error_exception:
                return {"content": [{"type": "text", "text": f"Execution error initializing Apollo module track: {str(error_exception)}"}]}

        return {"content": [{"type": "text", "text": f"Error: Requested tool function '{tool_name}' is currently unsupported."}]}

    def run_stdio_transport_loop(self):
        """Listens continuously to standard input streams for incoming JSON-RPC protocol requests."""
        self.log_diagnostic("Goings OS master MCP connector listening via stdio channels.")
        
        while self.running:
            try:
                raw_line = sys.stdin.readline()
                if not raw_line:
                    break
                
                request = json.loads(raw_line)
                request_id = request.get("id")
                method = request.get("method")
                params = request.get("params", {})

                # Handle initialization handshakes and tools query requests
                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "Goings-OS-Master-MCP", "version": "1.0.0"}
                        }
                    }
                elif method == "tools/list":
                    response = {"jsonrpc": "2.0", "id": request_id, "result": self.list_available_tools()}
                elif method == "tools/call":
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})
                    execution_result = self.dispatch_tool_execution(tool_name, tool_args)
                    response = {"jsonrpc": "2.0", "id": request_id, "result": execution_result}
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Method function '{method}' not discovered."}
                    }

                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except Exception as process_exception:
                self.log_diagnostic(f"Critical error encountered in stdio parsing stream: {str(process_exception)}")

if __name__ == "__main__":
    # Initialize the server instance to run the continuous transport listener
    server = GoingsOsMcpServer()
    server.run_stdio_transport_loop()
