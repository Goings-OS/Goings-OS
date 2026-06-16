# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UNIFIED OMNI-CLI SUBPROCESS INTERACTION CONTROLLER
# COMPLIANCE: ZERO EM-DASHES; WAL CONCURRENCY LOGGING; NATIVE BINARY CHECKING
# ==============================================================================

import json
import logging
import os
import shutil
import sqlite3
import subprocess
import sys
import time

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class OmniCLIWrapper:
    """Orchestrates seamless inter-process communication between gh, firebase, and gcloud CLIs."""

    def __init__(self):
        self.root_dir = os.getenv("GOINGS_OS_ROOT", os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(self.root_dir, "goings_os_vault.db")
        self.humanitarian_db = os.path.join(self.root_dir, "choice_legacy_vault.db")
        self.log_path = os.path.join(self.root_dir, "system_faults.log")
        
        # Hardcoded Corporate Parameters for Strategic Financial Reporting
        self.weekly_revenue_floor = 5000.00
        self.tbe_base_retainer = 3500.00
        self.laec_min_booking = 2500.00
        self.choice_grant_block = 10000.00

        logging.basicConfig(
            filename=self.log_path,
            level=logging.ERROR,
            format="%(asctime)s UTC // OMNI_CLI_WRAPPER_FAULT // %(message)s"
        )
        self._initialize_telemetry_table()

    def _initialize_telemetry_table(self):
        """Prepares the database schema and forces WAL mode for high-concurrency loops."""
        for path in [self.db_path, self.humanitarian_db]:
            try:
                connection = sqlite3.connect(path, timeout=30.0)
                cursor = connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cli_orchestration_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        cli_binary TEXT,
                        command_executed TEXT,
                        return_code INTEGER,
                        execution_summary TEXT
                    )
                """)
                connection.commit()
                connection.close()
            except sqlite3.Error as fault:
                logging.error(f"Failed to clear WAL database paths for wrapper operations: {str(fault)}")

    def verify_and_log_binary_presence(self, binary_name: str) -> bool:
        """Checks if the command utility is correctly configured inside your system environment paths."""
        binary_path = shutil.which(binary_name)
        status = binary_path is not None
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        summary = f"Binary path found: {binary_path}" if status else "Binary missing or path environment unconfigured"
        
        target_db = self.db_path
        if "choice" in binary_name.lower():
            target_db = self.humanitarian_db
        try:
            connection = sqlite3.connect(target_db, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO cli_orchestration_log (timestamp, cli_binary, command_executed, return_code, execution_summary)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, binary_name, "ENVIRONMENT_PATH_CHECK", 0 if status else 1, summary))
            connection.commit()
            connection.close()
        except sqlite3.Error as write_fault:
            logging.error(f"Failed to record environment check parameters: {str(write_fault)}")
            
        return status

    def execute_cli_handshake(self, binary_name: str, arguments: list) -> dict:
        """Executes terminal commands safely using subprocess wrappers and captures output frames."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        full_command = [binary_name] + arguments
        command_string = " ".join(full_command)
        
        if not shutil.which(binary_name):
            return {"status": "FAILED", "reason": f"Binary tool {binary_name} is uninstalled or unreachable."}

        try:
            result = subprocess.run(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=45.0,
                cwd=self.root_dir
            )
            
            return_code = result.returncode
            summary_output = result.stdout.strip() if return_code == 0 else result.stderr.strip()
            
            target_db = self.db_path
            if "choice" in binary_name.lower() or "choice" in str(arguments).lower():
                target_db = self.humanitarian_db
            connection = sqlite3.connect(target_db, timeout=30.0)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO cli_orchestration_log (timestamp, cli_binary, command_executed, return_code, execution_summary)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, binary_name, command_string, return_code, summary_output[:200]))
            connection.commit()
            connection.close()
            
            return {
                "status": "SUCCESS" if return_code == 0 else "ERROR_RETURNED",
                "code": return_code,
                "output_payload": summary_output
            }
            
        except subprocess.TimeoutExpired:
            logging.error(f"Command execution timeout crossed: {command_string}")
            return {"status": "TIMEOUT", "reason": "Execution period exceeded 45 seconds."}
        except Exception as hardware_fault:
            logging.error(f"System environment connection error: {str(hardware_fault)}")
            return {"status": "HARDWARE_EXCEPTION", "reason": str(hardware_fault)}


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS UNIFIED OMNI-CLI CONTROLLER CORE ")
    print("==========================================================")
    
    wrapper = OmniCLIWrapper()
    target_utilities = ["gh", "firebase", "gcloud"]
    for utility in target_utilities:
        available = wrapper.verify_and_log_binary_presence(utility)
        print(f" -> Checking Terminal Interface [{utility}]: {'OPERATIONAL' if available else 'PATH_UNCONFIGURED'}")
        
    print("\n📡 Initiating Secure GitHub Cloud Sync Handshake...")
    github_check = wrapper.execute_cli_handshake("gh", ["auth", "status"])
    print(f" -> Operation Signal State: {github_check['status']}")
    print("==========================================================")