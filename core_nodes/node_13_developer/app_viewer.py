import os
import sqlite3
import http.server
import socketserver
import json

class LocalAppDashboard:
    def __init__(self):
        self.db_path = r"core_nodes\node_08_vault\saas_storage.db"
        self.web_dir = r"core_nodes\node_13_developer\web_app"
        self.port = 8080

    def compile_html_assets(self):
        """Generates a clean web dashboard template to view local database metrics."""
        if not os.path.exists(self.web_dir):
            os.makedirs(self.web_dir)

        # Pull active mock records from your verified sqlite file storage
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_list = [t[0] for t in tables]
        
        records_html = ""
        if "mock_tenant_leads" in table_list:
            cursor.execute("SELECT * FROM mock_tenant_leads")
            rows = cursor.fetchall()
            for row in rows:
                records_html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
        else:
            records_html = "<tr><td colspan='3'>No active student or tenant records found.</td></tr>"
            
        connection.close()

        html_content = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>GOINGS OS: PLATFORM VIEWPORT</title>
            <style>
                body {{ background-color: #0b0c10; color: #c5a059; font-family: 'Courier New', monospace; padding: 30px; }}
                h1 {{ border-bottom: 2px solid #c5a059; padding-bottom: 10px; font-size: 24px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #1f2833; }}
                th, td {{ padding: 12px; text-align: left; border: 1px solid #c5a059; }}
                th {{ background-color: #c5a059; color: #0b0c10; }}
                .status {{ color: #4eed50; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>??? GOINGS OS: OPERATIONAL MONITOR DISPLAY</h1>
            <p>SYSTEM MATRIX XP STATUS: <span class="status">18,664 XP ACTIVE</span></p>
            <p>VAULT LOCATION: core_nodes/node_08_vault/saas_storage.db</p>
            <table>
                <thead>
                    <tr><th>LEAD ID TOKEN</th><th>TENANT IDENTIFIER UUID</th><th>ENCRYPTED ACCOUNT EMAIL</th></tr>
                </thead>
                <tbody>
                    {records_html}
                </tbody>
            </table>
        </body>
        </html>
        """
        
        with open(os.path.join(self.web_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[APP] Visual interface template written to: {self.web_dir}")

    def launch_local_server(self):
        """Spins up a lightweight background network server port to render your app screen."""
        self.compile_html_assets()
        os.chdir(self.web_dir)
        
        Handler = http.server.SimpleHTTPRequestHandler
        print(f"\n[SUCCESS] Goings OS App Viewport is live on your machine.")
        print(f"?? ACTION REQUIRED: Open your web browser and go to: http://localhost:{self.port}\n")
        
        # Open port 8080 to render the local file system interface
        with socketserver.TCPServer(("", self.port), Handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[SYS] Visual dashboard app server safely spun down.")

if __name__ == "__main__":
    app = LocalAppDashboard()
    app.launch_local_server()
