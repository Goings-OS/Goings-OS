import sys
import requests

# 🛡️ DUAL-NODE FLEET CONFIGURATION
NODES = [
    "https://script.google.com/macros/s/AKfycbymym3cs-xXkCNcSkWRzOctJBA8AB3vv8HR5lXNAI8dbNoEFALbxioXcA253B61G60etg/exec",
    "https://script.google.com/macros/s/AKfycbxnltQx8Lq6kQhv56aXx8FFO7k29Rs2fwDb1J5bIpz-iGruGFNO9urdRubsl7lK0xYv/exec"
]

def execute_strike(name, rep="DIRECT", status="Interested"):
    print(f"🚀 NTC 400 COCKPIT: Initiating Strike for -> {name}")
    # Defining the Full Stack Payload
    payload = {
        "full_name": name,
        "rep_name": rep,
        "status": status,
        "total_value": 0
    }
    
    for i, url in enumerate(NODES, 1):
        try:
            print(f"📡 NODE {i:02}: Transmitting...")
            response = requests.post(url, json=payload, timeout=15)
            print(f"✅ NODE {i:02} HUD: {response.text}")
        except Exception as e:
            print(f"❌ NODE {i:02} CONNECTION FAILED: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Join name arguments into a single string
        target_name = " ".join(sys.argv[1:])
        execute_strike(target_name)
    else:
        print("⚠️ COMMANDER: No name provided.")
        print("Usage: python3 swarm_commander.py 'Patriot Name'")
