# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# SCRIPT: VERIFY DRIVE LIVE AUDIT (verify_drive_live.py)
# UPGRADE: AUTO DISCOVERY AND SELF HEALING VAULT PROVISIONER
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS
# ==============================================================================

import os
import sys
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

# Ensure repository root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from node_08_vault.client_warehouse import ClientWarehouseEngine

VAULT_FOLDER_NAME = "Goings OS Vault"
SHARE_TARGET_EMAIL = "info@goingsos.com"
CLIENT_ID = "CLI_757_001"
CLIENT_NAME = "Marcus Vance"
OPERATOR_ID = "Architect_Terrence"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]

def load_credentials():
    """Loads credentials checking service_account.json first then ADC with drive scope."""
    sa_path = os.path.join(BASE_DIR, "service_account.json")
    env_sa = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    
    if env_sa and os.path.exists(env_sa):
        try:
            creds = service_account.Credentials.from_service_account_file(env_sa, scopes=SCOPES)
            return creds, f"Service Account (Env): {creds.service_account_email}"
        except Exception:
            pass

    if os.path.exists(sa_path):
        try:
            creds = service_account.Credentials.from_service_account_file(sa_path, scopes=SCOPES)
            return creds, f"Service Account: {creds.service_account_email}"
        except Exception:
            pass

    creds, _ = google.auth.default(scopes=SCOPES)
    if hasattr(creds, "with_scopes"):
        try:
            creds = creds.with_scopes(SCOPES)
        except Exception:
            pass
            
    identity = getattr(creds, "service_account_email", None) or "Application Default Credentials (ADC)"
    return creds, identity


def resolve_vault_folder(drive):
    """Auto discovers existing 'Goings OS Vault' or self heals by creating and sharing one."""
    search_query = f"name = '{VAULT_FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    print(f"Auto Discovery: Searching Drive for folder named '{VAULT_FOLDER_NAME}'...")

    results = drive.files().list(
        q=search_query,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        fields="files(id, name, webViewLink, capabilities)"
    ).execute()

    folders = results.get("files", [])

    if folders:
        matched = folders[0]
        folder_id = matched.get("id")
        folder_url = matched.get("webViewLink", f"https://drive.google.com/drive/folders/{folder_id}")
        print(f"SUCCESS: Auto Discovered existing '{VAULT_FOLDER_NAME}'")
        print(f"True Resolved Folder ID: {folder_id}")
        print(f"Folder Web Link: {folder_url}")
        return folder_id, folder_url, False

    # Self Healing: Create root folder named 'Goings OS Vault'
    print(f"Folder '{VAULT_FOLDER_NAME}' not found. Initializing Self Healing Provisioner...")
    folder_metadata = {
        "name": VAULT_FOLDER_NAME,
        "mimeType": "application/vnd.google-apps.folder"
    }

    created = drive.files().create(
        body=folder_metadata,
        fields="id, name, webViewLink",
        supportsAllDrives=True
    ).execute()

    folder_id = created.get("id")
    folder_url = created.get("webViewLink", f"https://drive.google.com/drive/folders/{folder_id}")
    print(f"SUCCESS: Self Healed and Created Root Folder '{VAULT_FOLDER_NAME}'")
    print(f"True Resolved Folder ID: {folder_id}")
    print(f"Folder Web Link: {folder_url}")

    # Share with info@goingsos.com with role='writer'
    print(f"Sharing '{VAULT_FOLDER_NAME}' with {SHARE_TARGET_EMAIL} as writer...")
    try:
        permission_payload = {
            "type": "user",
            "role": "writer",
            "emailAddress": SHARE_TARGET_EMAIL
        }
        drive.permissions().create(
            fileId=folder_id,
            body=permission_payload,
            supportsAllDrives=True
        ).execute()
        print(f"SUCCESS: Shared folder with {SHARE_TARGET_EMAIL} (role: writer)")
    except Exception as perm_err:
        print(f"Notice during permission assignment: {perm_err}")

    return folder_id, folder_url, True


def main():
    print("=" * 70)
    print("GOINGS OS // GOOGLE DRIVE AUTO DISCOVERY AND SELF HEALING ONBOARDING")
    print("=" * 70)

    try:
        creds, identity = load_credentials()
        print(f"Authenticated Identity: {identity}")
    except Exception as auth_err:
        print(f"FAILED: Unable to load credentials: {auth_err}")
        return

    drive = build("drive", "v3", credentials=creds)

    try:
        resolved_folder_id, resolved_folder_url, was_created = resolve_vault_folder(drive)
    except Exception as drive_err:
        print(f"FAILED: Google Drive resolution error: {drive_err}")
        return

    print("-" * 70)
    print(f"Executing ClientWarehouseEngine.onboard_client for {CLIENT_ID}...")
    print(f"Target Parent Folder ID: {resolved_folder_id}")

    try:
        engine = ClientWarehouseEngine(enable_live_google_apis=True)
        res = engine.onboard_client(
            client_id=CLIENT_ID,
            client_name=CLIENT_NAME,
            operator_id=OPERATOR_ID,
            parent_folder_id=resolved_folder_id,
            initial_documents=[{
                "name": "Retainer_Agreement.pdf",
                "content": b"Sample Signed Contract Content for Marcus Vance",
                "category": "Intake"
            }]
        )

        print("-" * 70)
        print("ONBOARDING EXECUTION COMPLETED")
        print(f"Status: {res.get('status')}")
        print(f"Client ID: {res.get('client_id')}")
        print(f"Client Name: {res.get('client_name')}")

        folders = res.get("folders", {})
        print(f"Root Client Folder ID: {folders.get('root_folder_id')}")
        print(f"Root Client Folder URL: {folders.get('root_folder_url')}")
        print(f"Storage Mode: {folders.get('storage_mode')}")

        print("Standardized Five Folder Hierarchy:")
        subfolders = folders.get("subfolders", {})
        for sub_name, sub_info in subfolders.items():
            print(f"  * {sub_name}:")
            print(f"      ID:  {sub_info.get('folder_id')}")
            print(f"      URL: {sub_info.get('folder_url')}")

        stamps = res.get("compliance_stamps", [])
        print(f"Compliance Stamps Generated: {len(stamps)}")
        for stamp in stamps:
            print(f"  * Stamp ID: {stamp.get('stamp_id')}")
            print(f"    Document: {stamp.get('document_name')}")
            print(f"    SHA-256:  {stamp.get('sha256_hash')}")
            print(f"    Citation: {stamp.get('statutory_citation')}")

    except Exception as exec_err:
        print(f"FAILED: Onboarding execution error: {exec_err}")

    print("=" * 70)


if __name__ == "__main__":
    main()
