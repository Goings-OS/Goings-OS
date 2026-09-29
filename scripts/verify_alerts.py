# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# SCRIPT: VERIFY ALERT CHANNELS (scripts/verify_alerts.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS
# ==============================================================================

import os
import sys
import requests
from dotenv import load_dotenv

# Ensure stdout uses UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore
    except AttributeError:
        pass

# Force reload from .env in root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(root_dir, ".env")
load_dotenv(env_path, override=True)

tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
tg_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
gchat_webhook = os.getenv("GOOGLE_CHAT_AUTO_UPDATE_WEBHOOK", "").strip()

print("==============================================================")
print(" GOINGS OS v4.2 // LIVE ALERT DISPATCH VERIFICATION           ")
print("==============================================================")
print(f"Loaded .env from: {env_path}")
print(f"Telegram Token Configured: {bool(tg_token)} ({tg_token[:6]}... if set)")
print(f"Telegram Chat ID Configured: {bool(tg_chat_id)}")
print(f"Google Chat Webhook Configured: {bool(gchat_webhook)} ({gchat_webhook[:25]}... if set)")
print("--------------------------------------------------------------")

# 1. Telegram Verification
if tg_token and tg_chat_id:
    tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    tg_payload = {
        "chat_id": tg_chat_id,
        "text": "Goings OS Gateway Online! Live alert dispatch verified successfully.",
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(tg_url, json=tg_payload, timeout=10.0)
        print(f"[TELEGRAM] HTTP Status: {resp.status_code}")
        if resp.status_code == 200:
            print("[TELEGRAM] Message delivered successfully to Telegram!")
        else:
            print(f"[TELEGRAM] Error response: {resp.text}")
    except Exception as e:
        print(f"[TELEGRAM] Connection error: {str(e)}")
else:
    print("[TELEGRAM] SKIPPED: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is empty in .env.")

# 2. Google Chat Verification
if gchat_webhook:
    gchat_payload = {
        "text": "Goings OS Gateway Online! Live alert dispatch verified successfully."
    }
    try:
        resp = requests.post(gchat_webhook, json=gchat_payload, timeout=10.0)
        print(f"[GOOGLE CHAT] HTTP Status: {resp.status_code}")
        if resp.status_code == 200:
            print("[GOOGLE CHAT] Message delivered successfully to Google Chat Space!")
        else:
            print(f"[GOOGLE CHAT] Error response: {resp.text}")
    except Exception as e:
        print(f"[GOOGLE CHAT] Connection error: {str(e)}")
else:
    print("[GOOGLE CHAT] SKIPPED: GOOGLE_CHAT_AUTO_UPDATE_WEBHOOK is empty in .env.")

print("==============================================================")
