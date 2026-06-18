import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

class GoogleWorkspaceAuthGateway:
    def __init__(self):
        # Request access to Drive and Slides to facilitate the Vids translation layer
        self.scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/slides"
        ]
        self.credentials_json = "client_secret.json"
        self.token_json = "core_nodes/node_16_media_orchestrator/token.json"

    def authenticate_session(self):
        """Resolves existing authorization state or establishes a new web based handshake."""
        creds = None
        
        # Ingest existing session token if persistent on disk
        if os.path.exists(self.token_json):
            print("[AUTH] Restoring background token state from token.json...")
            creds = Credentials.from_authorized_user_file(self.token_json, self.scopes)
            
        # Refresh or initialize tokens cleanly
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("[AUTH] Access token expired. Requesting refresh routine...")
                creds.refresh(Request())
            else:
                print("[AUTH] No valid session token detected. Initializing OAuth2 flow...")
                if not os.path.exists(self.credentials_json):
                    print(f"[CRITICAL ERROR] Please download {self.credentials_json} from the Google Cloud Console.")
                    sys.exit(1)
                    
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_json, self.scopes)
                creds = flow.run_local_server(port=0)
                
            # Write token to local tracking path for future silent daemon execution
            with open(self.token_json, "w") as token_file:
                token_file.write(creds.to_json())
                
        print("[SUCCESS] Google Workspace core credentials fully authorized and secured.")
        return creds

if __name__ == "__main__":
    gateway = GoogleWorkspaceAuthGateway()
    gateway.authenticate_session()
