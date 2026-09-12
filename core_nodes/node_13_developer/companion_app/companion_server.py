import http.server
import socketserver
import json
import os

PORT = 5000
DIRECTORY = os.path.join('core_nodes', 'node_13_developer', 'companion_app', 'web_root')

class GenUiServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def do_GET(self):
        if self.path in ("/notebook_studio", "/notebook_studio.html"):
            template_path = os.path.join('core_nodes', 'node_13_developer', 'companion_app', 'templates', 'notebook_studio.html')
            if os.path.exists(template_path):
                with open(template_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Template Not Found")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers['Content-Length'])
            req = json.loads(self.rfile.read(content_length).decode('utf-8'))
            user_text = req.get('text', '').lower()
            
            reply = "I have verified your query, Commander. Standing by for specific module initialization."
            component = "<p style='color:#888;text-align:center;'>[System Idle]</p>"
            
            if "price" in user_text or "tier" in user_text or "charge" in user_text:
                reply = "Displaying your high-ticket service layers directly on the interface, Commander."
                component = "<h3 style='color:#d4af37;margin-top:0;'>Keep It Goings LLC Ledger</h3><table style='width:100%;font-size:12px;border-collapse:collapse;' border='1' bordercolor='#333'><tr style='background:#111;'><th>Product</th><th>Fee</th><th>Target</th></tr><tr><td>Credit Clarity</td><td>$500</td><td>15 USC 1681e(b)</td></tr><tr><td>Freedom Accelerator</td><td>$1000</td><td>15 USC 1681s-2(b)</td></tr><tr><td>Insolvency Audit</td><td>$1500</td><td>15 USC 1681g</td></tr></table>"
            
            elif "grant" in user_text or "sam" in user_text or "choice" in user_text:
                reply = "Launching your active capital tracking module for Choice, targeting 350 families."
                component = "<h3 style='color:#4a90e2;margin-top:0;'>Choice Grant Tracking Matrix</h3><ul style='font-size:12px;margin:0;padding-left:20px;'><li><b>SAM.gov Portal:</b> Youth STEM Infrastructure Grant (Staged)</li><li><b>Grants.gov Portal:</b> Community Empowerment Fund (Active)</li><li><b>Target Threshold:</b> 350 Regional Families Accounted For</li></ul>"
            
            elif "website" in user_text or "build" in user_text or "prototype" in user_text:
                reply = "Initializing the automated web prototyping module. Deploying your reactive onyx and gold architecture framework lines now."
                component = "<h3 style='color:#d4af37;margin-top:0;'>GOINGS OS // WEB GENERATION TERMINAL</h3><div style='background:#111;border:1px solid #d4af37;padding:12px;border-radius:4px;font-family:monospace;font-size:11px;'><p style='color:#4eed50;margin:0;'>[STATUS] Compiling React Front-End Container...</p><p style='color:#fff;margin:5px 0;'>-> Domain Linked: keepitgoings.com</p><p style='color:#fff;margin:5px 0;'>-> Design Stack: Tailwind CSS Grid // Premium Inter Typography</p><p style='color:#888;margin:5px 0 0 0;'>[IaC Core] Containerized bundle is staging for serverless Firebase deploy.</p></div>"
                
            payload = json.dumps({"reply": reply, "component": component}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), GenUiServerHandler) as httpd:
        print('\n[GEN-UI INTERFACE SERVER RUNNING NATIVELY ON PORT 5000...]')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n[SYS] Server safely down.')