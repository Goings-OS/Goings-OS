import os

def run_pre_flight_check():
    manifest_file = "core_nodes/node_17_agent_orchestrator/presentation_manifest.md"
    print("[PRE-FLIGHT] Commencing systemic component validation...")
    
    if os.path.exists(manifest_file):
        print("[PRE-FLIGHT SUCCESS] Presentation manifest located cleanly on disk.")
        return True
    else:
        print("[PRE-FLIGHT ALERT] Blueprint manifest missing from target path.")
        return False

if __name__ == "__main__":
    run_pre_flight_check()
