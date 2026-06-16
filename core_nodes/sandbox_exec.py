import os
import sys
import tempfile
import subprocess

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class SafeSandbox:
    """Provides isolated subprocess execution containers to validate worker gem code payloads."""

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def is_safe_code(self, code_str: str) -> tuple[bool, str]:
        """Performs static inspection on the source code string to block dangerous operations."""
        restricted_phrases = [
            "__import__", "eval(", "exec(", "open(", "import os", "import sys",
            "import subprocess", "import shutil", "import importlib", "os.system",
            "subprocess.run", "subprocess.Popen", "shutil.rmtree"
        ]
        
        for phrase in restricted_phrases:
            if phrase in code_str:
                return False, f"Static check failure: Restricted command '{phrase}' is blocked."
                
        return True, "Static check passed: Code is approved for sandboxed subprocess run."

    def run_code_isolated(self, code_str: str, timeout: float = 5.0) -> dict:
        """Executes the raw code string inside an isolated Python subprocess and traps outputs."""
        # 1. Run static analysis safety check
        is_safe, check_msg = self.is_safe_code(code_str)
        if not is_safe:
            return {
                "success": False,
                "output": "",
                "error": check_msg,
                "status": "BLOCKED_BY_SAFETY_GUARD"
            }

        # 2. Write code payload to a temporary file
        temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=".py", prefix="sandbox_", dir=self.temp_dir)
        try:
            with os.fdopen(temp_file_fd, "w", encoding="utf-8") as f:
                f.write(code_str)
            
            # 3. Spawn isolated subprocess using the active python interpreter executable
            result = subprocess.run(
                [sys.executable, temp_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout.strip(),
                    "error": "",
                    "status": "COMPLETED_SUCCESSFULLY"
                }
            else:
                return {
                    "success": False,
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip(),
                    "status": "RUNTIME_EXCEPTION_TRIGGERED"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Timeout Exception: Code execution period exceeded {timeout} seconds.",
                "status": "TIMEOUT_EXCEEDED"
            }
        except Exception as hardware_fault:
            return {
                "success": False,
                "output": "",
                "error": f"Subprocess system failure: {str(hardware_fault)}",
                "status": "SYSTEM_FAULT"
            }
        finally:
            # 4. Enforce strict cleanup of the temporary file to prevent trace leakage
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS SAFE EXECUTION SANDBOX CORE        ")
    print("==========================================================")
    
    sandbox = SafeSandbox()
    
    # Example 1: Run compliant code segment
    clean_code = "print('Hello from the private sandboxed container!')"
    print("Testing clean code execution...")
    res_clean = sandbox.run_code_isolated(clean_code)
    print(f" -> Status: {res_clean['status']}")
    print(f" -> Output: {res_clean['output']}")
    
    # Example 2: Run code with dangerous imports (blocked statically)
    dangerous_code = "import os\nos.system('dir')"
    print("\nTesting restricted code execution...")
    res_danger = sandbox.run_code_isolated(dangerous_code)
    print(f" -> Status: {res_danger['status']}")
    print(f" -> Error: {res_danger['error']}")
    
    # Example 3: Run code with syntax error
    syntax_error_code = "print('Unterminated string"
    print("\nTesting syntax error trapping...")
    res_syntax = sandbox.run_code_isolated(syntax_error_code)
    print(f" -> Status: {res_syntax['status']}")
    print(f" -> Error: {res_syntax['error']}")
    
    # Example 4: Run code with timeout loop
    infinite_loop_code = "import time\nwhile True:\n    pass"
    print("\nTesting timeout gate controls...")
    res_timeout = sandbox.run_code_isolated(infinite_loop_code, timeout=1.0)
    print(f" -> Status: {res_timeout['status']}")
    print(f" -> Error: {res_timeout['error']}")
    print("==========================================================")
