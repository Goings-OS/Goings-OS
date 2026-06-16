import os
import sys
import hmac
import hashlib
import json

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class GemIdentityManager:
    """Manages cryptographic agent authorization: token generation: and task validation loops."""

    def __init__(self, private_key: bytes = None):
        # Resolve private signing key from environment: falling back to a secure baseline default
        env_key = os.getenv("SWARM_PRIVATE_KEY")
        if env_key:
            self.private_key = env_key.encode("utf-8")
        else:
            self.private_key = private_key or b"default_goings_os_secure_signing_key_757"
            
        # Defining authorized identities inside the Goings OS framework
        self.authorized_gems = {
            "Architect": "Node 01: Prophet Architect Core",
            "Governor": "Level 3: Private Governor Controller",
            "Sentry": "Node 04: The Clerk / Sentry Identity Guard",
            "Worker": "Node 05: Task Worker Core Ingress",
            "Critic": "Node 15: Compliance Critic Evaluator"
        }

    def sign_task_node(self, task_id: str, intent: str, gem_identity: str) -> str:
        """Generates a secure HMAC-SHA256 signature token representing the authenticated task state."""
        if gem_identity not in self.authorized_gems:
            raise ValueError(f"Unauthorized gem identity check failed: {gem_identity}")

        # Prepare normalized task details for cryptographic hashing
        payload = {
            "task_id": task_id,
            "intent": intent,
            "gem_identity": gem_identity
        }
        # Force sort keys to guarantee identical serialization across execution nodes
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        
        # Compute HMAC signature token
        token = hmac.new(self.private_key, payload_bytes, hashlib.sha256).hexdigest()
        return token

    def verify_token(self, task_id: str, intent: str, gem_identity: str, token: str) -> bool:
        """Validates the cryptographic signature token to verify identity before execution runs."""
        if gem_identity not in self.authorized_gems:
            sys.stderr.write(f"Verification fail: Identity '{gem_identity}' is not in authorized list\n")
            return False

        try:
            expected_token = self.sign_task_node(task_id, intent, gem_identity)
            # Use constant-time comparison to prevent timing attack vulnerabilities
            is_valid = hmac.compare_digest(expected_token, token)
            return is_valid
        except Exception as err:
            sys.stderr.write(f"Verification process exception triggered: {str(err)}\n")
            return False


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS CRYPTOGRAPHIC AGENT IDENTITY CORE  ")
    print("==========================================================")
    
    manager = GemIdentityManager()
    
    # Simulate an Architect task signing pass
    task_id = "TASK-0491-SECURE"
    intent = "Update local firewall parameters"
    gem = "Architect"
    
    print(f"Signing task: {task_id} under gem role: {gem}")
    token = manager.sign_task_node(task_id, intent, gem)
    print(f" -> Generated HMAC-SHA256 Token: {token}")
    
    # Verify the generated token
    is_authenticated = manager.verify_token(task_id, intent, gem, token)
    print(f" -> Verification result: {'AUTHENTICATED' if is_authenticated else 'REJECTED'}")
    
    # Simulate tampering attempt
    tampered_intent = "Update local firewall parameters: disable compliance log"
    is_tampered_valid = manager.verify_token(task_id, tampered_intent, gem, token)
    print(f" -> Tampered task verification result: {'AUTHENTICATED' if is_tampered_valid else 'REJECTED_TAMPED'}")
    print("==========================================================")
