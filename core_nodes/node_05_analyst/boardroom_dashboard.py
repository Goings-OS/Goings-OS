# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: MORNING BOARDROOM VISUALIZATION DASHBOARD
# BIND: NODE 05 ANALYST // PORT 5002 EXECUTIVE RUNTIME
# COMPLIANCE: ZERO EM-DASHES ENFORCED // ALWAYS POSITIVE // EXPLICIT TYPING
# ==============================================================================

import os
import json
import http.server
import socketserver
from datetime import datetime, timezone
from threading import Thread

class BoardroomDashboardServer:
    """Serves the 6:00 AM multi-agent boardroom visualization matrix to the local network architecture."""

    def __init__(self, port: int = 5002) -> None:
        self.port: int = port
        self.output_directory: str = r"C:\Google\CloudSDK\Goings-OS\core_nodes\node_05_analyst"
        self.html_path: str = os.path.join(self.output_directory, "boardroom.html")
        self.initialize_dashboard_assets()

    def initialize_dashboard_assets(self) -> None:
        """Assembles the interactive HTML structure embedding Chart.js visualization arrays."""
        timestamp: str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        html_content: str = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Goings OS : Morning Boardroom Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-deep: #08060f;
            --bg-surface: #110e1c;
            --bg-card: #19152b;
            --gold-accent: #d4af37;
            --text-primary: #f1eef7;
            --text-secondary: #9a93b0;
            --border-purple: #251f3d;
        }}
        body {{
            background-color: var(--bg-deep);
            color: var(--text-primary);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 30px;
        }}
        .dashboard-header {{
            border-bottom: 1px solid var(--border-purple);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .dashboard-header h1 {{
            color: var(--gold-accent);
            margin: 0;
            font-size: 2.2rem;
            letter-spacing: 1px;
        }}
        .dashboard-header p {{
            color: var(--text-secondary);
            margin: 5px 0 0 0;
        }}
        .metrics-summary-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-purple);
            border-radius: 8px;
            padding: 20px;
            text-align: left;
        }}
        .metric-card h3 {{
            color: var(--text-secondary);
            margin: 0 0 10px 0;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .metric-card .value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--text-primary);
        }}
        .metric-card .subtext {{
            font-size: 0.8rem;
            color: var(--gold-accent);
            margin-top: 5px;
        }}
        .visualization-layout {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }}
        .chart-container {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-purple);
            border-radius: 12px;
            padding: 25px;
            min-height: 350px;
        }}
        .chart-container h2 {{
            color: var(--gold-accent);
            font-size: 1.2rem;
            margin-top: 0;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>

    <div class="dashboard-header">
        <h1>GOINGS OS : EXECUTIVE BOARDROOM</h1>
        <p>Simulation Tracking Matrix | Active Synchronization Window: {timestamp}</p>
    </div>

    <div class="metrics-summary-grid">
        <div class="metric-card">
            <h3>Total Ecosystem Capital</h3>
            <div class="value">$142,500.00</div>
            <div class="subtext">Across Multi-Pillar Accounts</div>
        </div>
        <div class="metric-card">
            <h3>Operations Runway</h3>
            <div class="value">$99,750.00</div>
            <div class="subtext">70% Programmatic Retention</div>
        </div>
        <div class="metric-card">
            <h3>Owner's Draw Ledger</h3>
            <div class="value">$42,750.00</div>
            <div class="subtext">30% Stream Allocation</div>
        </div>
        <div class="metric-card">
            <h3>Active Pipeline Leads</h3>
            <div class="value">342</div>
            <div class="subtext">Sourced Autonomously Via Scout</div>
        </div>
    </div>

    <div class="visualization-layout">
        <div class="chart-container">
            <h2>Treasury Rule Distribution Allocation</h2>
            <canvas id="treasuryChart"></canvas>
        </div>
        <div class="chart-container">
            <h2>Pillar Performance Metrics</h2>
            <canvas id="pillarChart"></canvas>
        </div>
    </div>

    <script>
        // Treasury Allocation Donut Chart Configurations
        const treasuryCtx = document.getElementById('treasuryChart').getContext('2d');
        new Chart(treasuryCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Operations Runway (70%)', "Owner's Draw Allocation (30%)"],
                datasets: [{{
                    data: [99750, 42750],
                    backgroundColor: ['#2e1a47', '#d4af37'],
                    borderColor: '#110e1c',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#f1eef7' }} }}
                }}
            }}
        }});

        // Pillar Performance Bar Chart Configurations
        const pillarCtx = document.getElementById('pillarChart').getContext('2d');
        new Chart(pillarCtx, {{
            type: 'bar',
            data: {{
                labels: ['Goings OS', 'Tanita Brinkley Enterprises', 'the nightlife (LAEC)', 'Choice Inc.'],
                datasets: [{{
                    label: 'Gross Generation Yield ($)',
                    data: [55000, 42000, 31000, 14500],
                    backgroundColor: '#d4af37',
                    borderColor: '#251f3d',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{ ticks: {{ color: '#9a93b0' }}, grid: {{ color: '#251f3d' }} }},
                    y: {{ ticks: {{ color: '#9a93b0' }}, grid: {{ color: '#251f3d' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write(html_content.strip() + "\n")
        print(f"[COMPILED] Dashboard UI initialized successfully at: {self.html_path}")

    def start_local_server(self) -> None:
        """Launches the lightweight background server thread on localized port tracks."""
        os.chdir(self.output_directory)
        handler = http.server.SimpleHTTPRequestHandler
        
        # Eliminate port binding conflicts during rapid restarts
        socketserver.TCPServer.allow_reuse_address = True
        
        with socketserver.TCPServer(("", self.port), handler) as server:
            print(f"[ACTIVE] Boardroom Visualization interface running at http://localhost:{self.port}/boardroom.html")
            server.serve_forever()

if __name__ == "__main__":
    dashboard = BoardroomDashboardServer(port=5002)
    # Spin up the listener instance inside a dedicated thread execution trace
    server_thread = Thread(target=dashboard.start_local_server, daemon=True)
    server_thread.start()
    
    # Keep the primary runtime script alive for process persistence
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Boardroom Dashboard server thread terminated cleanly.")
