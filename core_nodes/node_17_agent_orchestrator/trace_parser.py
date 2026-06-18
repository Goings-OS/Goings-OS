import traceback

class AutomatedTraceGate:
    def __init__(self):
        self.system_mode = "AUTONOMOUS_DEBUG"

    def execute_and_capture_faults(self, target_function, *args, **kwargs):
        """Runs your local scripts and captures any raw trace data for immediate agent processing."""
        try:
            print("[EXECUTION RUN] Initializing active script module...")
            return target_function(*args, **kwargs)
        except Exception as system_fault:
            print("[CRITICAL FAULT DETECTED] Intercepting error state...")
            
            # Extract the raw, unedited stack trace string from the terminal
            raw_stack_trace = traceback.format_exc()
            print("[TRACE CAPTURE SUCCESS] Passing log dump straight to your agent for automated repair.")
            
            payload_for_agent = {
                "error_type": type(system_fault).__name__,
                "stack_trace_log": raw_stack_trace,
                "action_requirement": "Refactor local parameters to resolve this execution error."
            }
            return payload_for_agent
