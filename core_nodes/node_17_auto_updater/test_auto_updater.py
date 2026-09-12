# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: NODE 17 PYTEST SUITE (core_nodes/node_17_auto_updater/test_auto_updater.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; ENTERPRISE TESTING
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

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core_nodes.node_17_auto_updater.notifier import MultiChannelNotifier
from core_nodes.node_17_auto_updater.auto_updater import (
    ReleaseFeedScanner,
    AutonomousUpdateEngine
)
from ingress_gateway import app


class TestReleaseFeedScanner(unittest.TestCase):
    """Verifies scanner polling and configuration diffing."""

    def setUp(self):
        self.scanner = ReleaseFeedScanner()

    def test_poll_pypi_dependencies(self):
        res = self.scanner.poll_pypi_dependencies(["fastapi", "pydantic"])
        assert "fastapi" in res
        assert "pydantic" in res
        assert res["fastapi"].get("latest_version") is not None

    def test_poll_google_cloud_release_notes(self):
        notes = self.scanner.poll_google_cloud_release_notes()
        assert isinstance(notes, list)
        assert len(notes) > 0
        assert any(n.get("product") == "Cloud Run" for n in notes)

    def test_poll_gemini_api_changelog(self):
        changelog = self.scanner.poll_gemini_api_changelog()
        assert isinstance(changelog, list)
        assert len(changelog) > 0
        models = [item.get("model") for item in changelog]
        assert "gemini-3.8-flash" in models

    def test_diff_findings_generation(self):
        findings = {
            "google_cloud_notes": [
                {
                    "severity": "SECURITY",
                    "actionable": True,
                    "recommended_patterns": ["novel_threat_signature_alpha"]
                }
            ],
            "gemini_changelogs": [
                {"model": "gemini-nextgen-speed"}
            ],
            "pypi_dependencies": {
                "fastapi": {"latest_version": "99.0.0"}
            }
        }
        patches = self.scanner.diff_findings(findings)
        assert isinstance(patches, list)
        assert len(patches) >= 2
        types = [p.get("type") for p in patches]
        assert "SECURITY_SIGNATURE_UPDATE" in types


class TestAutonomousUpdateEngine(unittest.TestCase):
    """Verifies branch creation, patch application, and self-healing loop."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = AutonomousUpdateEngine(root_dir=self.temp_dir, secret_key="test_secret_abc")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_isolated_branch(self):
        branch = self.engine.create_isolated_branch(date_str="2026-09-12")
        assert branch == "auto-update/2026-09-12"

    def test_apply_patches(self):
        patch_list = [
            {
                "target_file": os.path.join(self.temp_dir, "config.py"),
                "diff_summary": "+ patched_signature = True",
                "description": "Apply security signature"
            }
        ]
        result = self.engine.apply_patches(patch_list)
        assert result["status"] == "APPLIED"
        assert result["patches_count"] == 1
        assert "Apply security signature" in result["applied"]

    def test_approval_token_and_url_generation(self):
        ts = int(time.time())
        branch = "auto-update/2026-09-12"
        token = self.engine.generate_signed_approval_token(branch=branch, timestamp=ts, nonce="nonce999")
        assert len(token) == 64

        url = self.engine.construct_approval_url(
            base_url="https://api.goingsos.com",
            branch=branch,
            timestamp=ts,
            nonce="nonce999"
        )
        assert "https://api.goingsos.com/api/v4.2/deploy/approve?" in url
        assert f"token={token}" in url

    def test_self_healing_loop_success(self):
        attempts = 0

        def mock_verify(test_file=None):
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                return False, "Simulated fault on attempt 1"
            return True, "Simulated pass on attempt 2"

        with patch.object(self.engine, "run_verification_checks", side_effect=mock_verify):
            passed, history = self.engine.execute_self_healing_loop(max_retries=3)
            assert passed is True
            assert len(history) == 2
            assert history[0]["status"] == "FAILED"
            assert history[1]["status"] == "PASSED"

    def test_run_dry_run_generation(self):
        dry_run = self.engine.run_dry_run()
        assert dry_run["dry_run"] is True
        assert dry_run["status"] == "SUCCESS"
        assert "approval_url" in dry_run
        assert dry_run["google_chat_card_generated"] is True
        assert "cardsV2" in dry_run["chat_card_preview"]

    def test_execute_daily_update_cycle(self):
        cycle_res = self.engine.execute_daily_update_cycle(
            base_url="https://api.goingsos.com"
        )
        assert cycle_res["status"] == "COMPLETED"
        assert cycle_res["tests_passed"] is True
        assert "approval_url" in cycle_res
        assert "alert_dispatch" in cycle_res


class TestMultiChannelNotifier(unittest.TestCase):
    """Verifies Google Chat card v2, Telegram push, and Voice escalation."""

    def setUp(self):
        self.notifier = MultiChannelNotifier()

    def test_build_google_chat_card(self):
        card = self.notifier.build_google_chat_card(
            title="Update Notification",
            summary="Package upgraded",
            diff_snippet="+ line",
            approval_url="https://example.com/approve",
            severity="INFO",
            branch="auto-update/2026-09-12"
        )
        assert "cardsV2" in card
        sections = card["cardsV2"][0]["card"]["sections"]
        assert len(sections) == 3

    def test_notify_deployment_approval(self):
        res = self.notifier.notify_deployment_approval(
            branch="auto-update/2026-09-12",
            timestamp=int(time.time()),
            client_ip="127.0.0.1"
        )
        assert "google_chat" in res
        assert "telegram" in res
        assert res["google_chat"]["status"] == "SIMULATED"
        assert res["telegram"]["status"] == "SIMULATED"

    def test_dispatch_alert_routing(self):
        res_crit = self.notifier.dispatch_alert(
            title="Critical Advisory",
            summary="Emergency patch",
            diff_snippet="+ patch",
            approval_url="https://example.com",
            severity="CRITICAL",
            branch="auto-update/2026-09-12"
        )
        assert "voice" in res_crit
        assert res_crit["voice"]["status"] == "SIMULATED"


class TestDeployApproveRoute(unittest.TestCase):
    """Verifies signed execution token approval route in ingress_gateway.py."""

    def setUp(self):
        self.client = TestClient(app)
        self.secret_key = os.environ.get("AUTO_UPDATE_SECRET", "goings_os_autonomous_deploy_secret_2026")

    def test_post_deploy_approve_success(self):
        branch = "auto-update/2026-09-12"
        ts = int(time.time())
        nonce = "nonce_post_456"
        msg = f"DEPLOY_BRANCH:{branch}:{ts}:{nonce}".encode("utf-8")
        token = hmac.new(self.secret_key.encode("utf-8"), msg, hashlib.sha256).hexdigest()

        response = self.client.post(
            "/api/v4.2/deploy/approve",
            json={
                "branch": branch,
                "token": token,
                "timestamp": str(ts),
                "nonce": nonce
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "APPROVED"
        assert data["action"] == "DEPLOY_MERGE_TRIGGERED"
        assert "notification_dispatch" in data
        assert data["notification_dispatch"]["google_chat"]["status"] == "SIMULATED"

    def test_post_deploy_approve_tampered_rejected(self):
        response = self.client.post(
            "/api/v4.2/deploy/approve",
            json={
                "branch": "auto-update/2026-09-12",
                "token": "invalid_bad_hash_token",
                "timestamp": str(int(time.time())),
                "nonce": "nonce_bad"
            }
        )
        assert response.status_code == 403


if __name__ == "__main__":
    unittest.main()
