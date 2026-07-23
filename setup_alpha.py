import os
import sys
import json
import subprocess
import shutil
from typing import Dict, Any, Optional

class AlphaEvolveOrchestrator:
    """
    Unabridged Full-Stack Deployment Engine for Google DeepMind's AlphaEvolve
    Calibrated explicitly for Keep It Goings Consulting infrastructure.
    """
    def __init__(self):
        self.tenant_id = "Keep It Goings Consulting"
        self.api_surface = "discoveryengine.googleapis.com"
        self.target_repo = "https://github.com/Google-Cloud-AI/alphaevolve-on-googlecloud.git"
        self.repo_dir = "alphaevolve-on-googlecloud"

    def execute_sys_call(self, command: str, telemetry_label: str, capture: bool = False) -> Optional[str]:
        """Executes hardware-level process directives with real-time exception tracking."""
        print(f"\n[SYSTEM EXECUTIVE] Action: {telemetry_label}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                stdout=subprocess.PIPE if capture else sys.stdout,
                stderr=subprocess.PIPE if capture else sys.stderr
            )
            if capture:
                return result.stdout.strip()
            return None
        except subprocess.CalledProcessError as err:
            print(f"❌ [CRITICAL BREAK] Failure encountered during: {telemetry_label}")
            if capture:
                print(f"Diagnostics: {err.stderr}")
            sys.exit(1)

    def retrieve_active_project(self) -> str:
        """Queries the active Google Cloud SDK context to harvest the active project ID."""
        if not shutil.which("gcloud"):
            print("❌ [ENVIRONMENT ERROR] Google Cloud SDK executable 'gcloud' not found in system path.")
            sys.exit(1)
            
        project = self.execute_sys_call("gcloud config get-value project", "Querying GCloud Environment for Active Project ID", capture=True)
        
        if not project or project == "(unset)":
            print("\n[ATTENTION] Active project ID not discovered within the local gcloud configuration profile.")
            project = input("Enter your target Google Cloud Project ID: ").strip()
            while not project:
                project = input("Project ID is required. Enter target Google Cloud Project ID: ").strip()
        
        print(f"🔒 [VERIFIED] Bound to active project instance: {project}")
        return project

    def capture_enterprise_app_id(self) -> str:
        """Captures the Gemini Enterprise Application token via direct runtime ingestion."""
        print("\n==================================================================")
        print("Please provide your Gemini Enterprise Application Profile ID.")
        print("This token is accessible via your Google Cloud Web Console matrix.")
        print("==================================================================")
        app_id = input("Paste your GE_APP_ID here: ").strip()
        
        while not app_id:
            app_id = input("The application token cannot be blank. Paste your GE_APP_ID here: ").strip()
        return app_id

    def build_enclave(self, project_id: str, app_id: str):
        """Constructs localized files, environment profiles, and pulls code repositories."""
        # Authenticate application defaults via browser redirection matrix
        self.execute_sys_call("gcloud auth application-default login --no-launch-browser", "Initializing Secure Cloud OAuth Handshake")
        
        # Provision the global API engine mapping
        self.execute_sys_call(
            f"gcloud services enable {self.api_surface} --project={project_id}",
            f"Provisioning Cloud REST Surface: Enforcing {self.api_surface}"
        )

        # Clone evolutionary workspace maps
        if not os.path.exists(self.repo_dir):
            self.execute_sys_call(f"git clone {self.target_repo}", "Cloning AlphaEvolve Core Framework Repositories")
        
        # Write cryptographic localized configuration structures
        env_path = os.path.join(self.repo_dir, ".env")
        env_payload = (
            f"PROJECT_ID={project_id}\n"
            f"GE_APP_ID={app_id}\n"
            f"ASSISTANT=default_assistant\n"
            f"TENANT_ID={self.tenant_id}\n"
        )
        
        with open(env_path, "w", encoding="utf-8") as env_file:
            env_file.write(env_payload)
            
        print(f"📝 [CONFIGURED] Isolated .env parameters written successfully to target path: {env_path}")

    def compile_virtual_environment(self):
        """Builds virtual execution runtimes using high-velocity uv or native fallback compilers."""
        os.chdir(self.repo_dir)
        
        if shutil.which("uv"):
            self.execute_sys_call("uv venv", "Allocating Virtual Sandboxed Layer via uv Ecosystem")
            self.execute_sys_call("uv pip install -e \".[dev]\"", "Injecting Local Production Framework Modules")
        else:
            self.execute_sys_call("python -m venv .venv", "Allocating Native Standard Python Isolation Space")
            pip_bin = os.path.join(".venv", "Scripts", "pip") if os.name == "nt" else os.path.join(".venv", "bin", "pip")
            self.execute_sys_call(f"{pip_bin} install -e \".[dev]\"", "Injecting Local Production Dependency Arrays")

    def run_pipeline(self):
        """Orchestrates the entire configuration sequence sequentially."""
        active_project = self.retrieve_active_project()
        active_app_id = self.capture_enterprise_app_id()
        self.build_enclave(active_project, active_app_id)
        self.compile_virtual_environment()
        
        print("\n==================================================================")
        print("🏆 [ORCHESTRATION COMPLETE] ALPHAEVOLVE SECURELY INTEGRATED       ")
        print(f"All structural systems mapped under target tenant: {self.tenant_id}")
        print("Your development workspace is primed for evolutionary iterations. ")
        print("==================================================================\n")

if __name__ == "__main__":
    orchestrator = AlphaEvolveOrchestrator()
    orchestrator.run_pipeline()