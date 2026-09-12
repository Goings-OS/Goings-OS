# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UNIT TESTS FOR AUTONOMOUS UPDATER (tests/test_auto_updater.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; ENTERPRISE UNITTEST
# ==============================================================================

import os
import sys
import time
import json
import hmac
import hashlib
import tempfile
import shutil
import urllib.parse
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Ensure workspace root is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core_nodes.node_17_auto_updater.notifier import MultiChannelNotifier
from core_nodes.node_17_auto_updater.auto_updater import (
    ReleaseFeedScanner,
    AutonomousUpdateEngine
)
from ingress_gateway import app


class TestReleaseFeedScanner(unittest.TestCase):
    """Verifies scanning and diffing logic across Google Cloud, Gemini, and PyPI."""

    def setUp(self):
        self.scanner = ReleaseFeedScanner()

    def test_poll_pypi_dependencies(self):
        result = self.scanner.poll_pypi_dependencies(["fastapi", "pydantic"])
        self.assertIn("fastapi", result)
        self.assertIn("pydantic", result)
        self.assertIsNotNone(result["fastapi"].get("latest_version"))

    def test_poll_google_cloud_release_notes(self):
        notes = self.scanner.poll_google_cloud_release_notes()
        self.assertIsInstance(notes, list)
        self.assertTrue(len(notes) > 0)
        self.assertTrue(any(n.get("product") == "Cloud Run" for n in notes))

    def test_poll_gemini_api_changelog(self):
        changelog = self.scanner.poll_gemini_api_changelog()
        self.assertIsInstance(changelog, list)
        self.assertTrue(len(changelog) > 0)
        models = [item.get("model") for item in changelog]
        self.assertIn("gemini-3.8-flash", models)

    def test_diff_findings_identifies_patches(self):
        findings = {
            "google_cloud_notes": [
                {
                    "severity": "SECURITY",
                    "actionable": True,
                    "recommended_patterns": ["novel_jailbreak_signature_xyz"]
                }
            ],
            "gemini_changelogs": [
                {
                    "model": "gemini-future-super-model-v99"
                }
            ],
            "pypi_dependencies": {
                "fastapi": {"latest_version": "99.0.0"}
            }
        }
        patches = self.scanner.diff_findings(findings)
        self.assertIsInstance(patches, list)
        self.assertTrue(len(patches) >= 2)
        patch_types = [p.get("type") for p in patches]
        self.assertIn("SECURITY_SIGNATURE_UPDATE", patch_types)
        self.assertIn("MODEL_UPGRADE", patch_types)


class TestAutonomousUpdateEngine(unittest.TestCase):
    """Verifies branch isolation, patch application, and self-healing loop."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = AutonomousUpdateEngine(root_dir=self.temp_dir, secret_key="test_secret_key_123")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_isolated_branch_format(self):
        branch = self.engine.create_isolated_branch(date_str="2026-09-12")
        self.assertEqual(branch, "auto-update/2026-09-12")

    def test_apply_patches(self):
        patches = [
            {
                "target_file": os.path.join(self.temp_dir, "test.py"),
                "diff_summary": "+ new signature line",
                "description": "Inject test signature"
            }
        ]
        res = self.engine.apply_patches(patches)
        self.assertEqual(res["status"], "APPLIED")
        self.assertEqual(res["patches_count"], 1)
        self.assertIn("Inject test signature", res["applied"])

    def test_signed_token_and_approval_url(self):
        ts = int(time.time())
        branch = "auto-update/2026-09-12"
        token = self.engine.generate_signed_approval_token(branch=branch, timestamp=ts, nonce="nonce123")
        self.assertTrue(len(token) == 64)

        approval_url = self.engine.construct_approval_url(
            base_url="https://api.goingsos.com",
            branch=branch,
            timestamp=ts,
            nonce="nonce123"
        )
        self.assertIn("https://api.goingsos.com/api/v4.2/deploy/approve?", approval_url)
        self.assertIn(f"branch={urllib.parse.quote(branch, safe='')}", approval_url)
        self.assertIn(f"token={token}", approval_url)

    def test_self_healing_execution_loop(self):
        # Mock run_verification_checks to fail twice and succeed on 3rd attempt
        call_count = 0

        def mock_verify(test_file=None):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return False, f"Traceback on attempt {call_count}: AssertionError in test"
            return True, "All tests passed successfully on attempt 3"

        with patch.object(self.engine, "run_verification_checks", side_effect=mock_verify):
            passed, history = self.engine.execute_self_healing_loop(max_retries=3)
            self.assertTrue(passed)
            self.assertEqual(len(history), 3)
            self.assertEqual(history[0]["status"], "FAILED")
            self.assertEqual(history[1]["status"], "FAILED")
            self.assertEqual(history[2]["status"], "PASSED")
            self.assertIn("gemini_3_8_flash_fix", history[0])

    def test_self_healing_execution_exhausts_retries(self):
        # Mock run_verification_checks to always fail
        def mock_always_fail(test_file=None):
            return False, "Persistent syntax error in module"

        with patch.object(self.engine, "run_verification_checks", side_effect=mock_always_fail):
            passed, history = self.engine.execute_self_healing_loop(max_retries=3)
            self.assertFalse(passed)
            self.assertEqual(len(history), 3)
            self.assertTrue(all(h["status"] == "FAILED" for h in history))


class TestMultiChannelNotifier(unittest.TestCase):
    """Verifies Google Chat cards, Telegram messages, and Voice escalation formatting."""

    def setUp(self):
        self.notifier = MultiChannelNotifier()

    def test_build_google_chat_card(self):
        card = self.notifier.build_google_chat_card(
            title="Security Patch Available",
            summary="Prompt injection defense updated",
            diff_snippet="+ blocked pattern",
            approval_url="https://api.goingsos.com/approve",
            severity="SECURITY",
            branch="auto-update/2026-09-12"
        )
        self.assertIn("cardsV2", card)
        sections = card["cardsV2"][0]["card"]["sections"]
        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0]["header"], "Update Diagnostics")
        self.assertEqual(sections[1]["header"], "Proposed Code Diff")
        self.assertEqual(sections[2]["header"], "Executive Action")

    def test_send_google_chat_simulated(self):
        res = self.notifier.send_google_chat(
            title="Test Update",
            summary="Summary of updates",
            diff_snippet="+ line",
            approval_url="https://example.com",
            severity="INFO"
        )
        self.assertEqual(res["status"], "SIMULATED")
        self.assertEqual(res["channel"], "google_chat")

    def test_send_telegram_simulated(self):
        res = self.notifier.send_telegram(
            title="Test Update",
            summary="Summary of updates",
            branch="auto-update/2026-09-12",
            severity="INFO",
            approval_url="https://example.com"
        )
        self.assertEqual(res["status"], "SIMULATED")
        self.assertEqual(res["channel"], "telegram")
        self.assertIn("inline_keyboard", res["payload"]["reply_markup"])

    def test_trigger_voice_call_simulated(self):
        res = self.notifier.trigger_voice_call("Critical alert message")
        self.assertEqual(res["status"], "SIMULATED")
        self.assertEqual(res["channel"], "voice")
        self.assertIn("<Say voice='Polly.Amy'>", res["twiml"])

    def test_dispatch_alert_coordination(self):
        # Non-critical severity should dispatch chat and telegram, not voice
        res_info = self.notifier.dispatch_alert(
            title="Daily Minor Update",
            summary="PyPI update available",
            diff_snippet="+ dependency",
            approval_url="https://example.com",
            severity="INFO",
            branch="auto-update/2026-09-12"
        )
        self.assertIn("google_chat", res_info)
        self.assertIn("telegram", res_info)
        self.assertNotIn("voice", res_info)

        # Critical severity MUST trigger voice escalation
        res_crit = self.notifier.dispatch_alert(
            title="Critical Security Threat",
            summary="Emergency zero day patch",
            diff_snippet="+ armor pattern",
            approval_url="https://example.com",
            severity="CRITICAL",
            branch="auto-update/2026-09-12"
        )
        self.assertIn("google_chat", res_crit)
        self.assertIn("telegram", res_crit)
        self.assertIn("voice", res_crit)


class TestDeployApproveEndpoint(unittest.TestCase):
    """Verifies /api/v4.2/deploy/approve route with signed execution tokens in ingress_gateway.py."""

    def setUp(self):
        self.client = TestClient(app)
        self.secret_key = os.environ.get("AUTO_UPDATE_SECRET", "goings_os_autonomous_deploy_secret_2026")

    def test_deploy_approve_success_get(self):
        branch = "auto-update/2026-09-12"
        ts = int(time.time())
        nonce = "nonce_abc_123"
        msg = f"DEPLOY_BRANCH:{branch}:{ts}:{nonce}".encode("utf-8")
        valid_token = hmac.new(self.secret_key.encode("utf-8"), msg, hashlib.sha256).hexdigest()

        response = self.client.get(
            "/api/v4.2/deploy/approve",
            params={
                "branch": branch,
                "token": valid_token,
                "timestamp": str(ts),
                "nonce": nonce
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "APPROVED")
        self.assertEqual(data["action"], "DEPLOY_MERGE_TRIGGERED")
        self.assertEqual(data["branch"], branch)

    def test_deploy_approve_success_post(self):
        branch = "auto-update/2026-09-12"
        ts = int(time.time())
        nonce = "nonce_post_789"
        msg = f"DEPLOY_BRANCH:{branch}:{ts}:{nonce}".encode("utf-8")
        valid_token = hmac.new(self.secret_key.encode("utf-8"), msg, hashlib.sha256).hexdigest()

        response = self.client.post(
            "/api/v4.2/deploy/approve",
            json={
                "branch": branch,
                "token": valid_token,
                "timestamp": str(ts),
                "nonce": nonce
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "APPROVED")

    def test_deploy_approve_tampered_token_rejected(self):
        branch = "auto-update/2026-09-12"
        ts = int(time.time())
        nonce = "nonce_post_789"
        bad_token = "deadbeef" * 8

        response = self.client.get(
            "/api/v4.2/deploy/approve",
            params={
                "branch": branch,
                "token": bad_token,
                "timestamp": str(ts),
                "nonce": nonce
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Invalid cryptographic execution token signature", response.json()["detail"])

    def test_deploy_approve_expired_token_rejected(self):
        branch = "auto-update/2026-09-12"
        # 48 hours ago
        ts = int(time.time()) - 172800
        nonce = "nonce_old"
        msg = f"DEPLOY_BRANCH:{branch}:{ts}:{nonce}".encode("utf-8")
        token = hmac.new(self.secret_key.encode("utf-8"), msg, hashlib.sha256).hexdigest()

        response = self.client.get(
            "/api/v4.2/deploy/approve",
            params={
                "branch": branch,
                "token": token,
                "timestamp": str(ts),
                "nonce": nonce
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("expired", response.json()["detail"].lower())

    def test_deploy_approve_missing_parameters_rejected(self):
        response = self.client.get(
            "/api/v4.2/deploy/approve",
            params={"branch": "auto-update/2026-09-12"}
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
