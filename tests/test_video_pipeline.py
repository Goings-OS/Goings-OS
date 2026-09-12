# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UNIT TESTS FOR VIDEO PRODUCTION ENGINE (tests/test_video_pipeline.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; UNITTEST ALIGNED
# ==============================================================================

import os
import sys
import shutil
import tempfile
import sqlite3
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image

# Ensure workspace root is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from node_09_catalyst import CatalystScriptEngine, pull_script_parameters
from node_15_elevenlabs import ElevenLabsAudioEngine, synthesize_voiceover
from node_16_media.video_pipeline import VideoProductionEngine, generate_mp4_container_bytes


class TestNode09Catalyst(unittest.TestCase):
    """Verifies Node 09 Catalyst script and storyboard extraction."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = CatalystScriptEngine(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_pull_script_parameters_luxury_affairs(self):
        params = self.engine.pull_script_parameters(
            campaign_id="TEST_LAEC_01",
            entity_name="Luxury Affairs Event Center"
        )
        self.assertEqual(params["campaign_id"], "TEST_LAEC_01")
        self.assertEqual(params["target_entity"], "Luxury Affairs Event Center")
        self.assertIn("Norfolk Takeover Cruise", params["focus_vector"])
        self.assertIn("Gold Metallic", params["visual_style_constraints"])
        self.assertIn("Scene 1", params["storyboard_sequence"])
        self.assertIn("target_audience", params)

    def test_pull_script_parameters_all_conglomerate_entities(self):
        entities = [
            "Keep It Goings LLC",
            "Tanita Brinkley Enterprises LLC",
            "Choice Inc",
            "Luxury Decor & Rentals LLC",
            "Norfolk Takeover Cruise LLC"
        ]
        for ent in entities:
            res = self.engine.pull_script_parameters(entity_name=ent)
            self.assertTrue(len(res["focus_vector"]) > 0)
            self.assertTrue(len(res["storyboard_sequence"]) > 0)
            self.assertIn("Scene", res["storyboard_sequence"])

    def test_convenience_helper(self):
        res = pull_script_parameters(campaign_id="TEST_HELPER", entity_name="Choice Inc")
        self.assertEqual(res["campaign_id"], "TEST_HELPER")
        self.assertIn("501(c)(3)", res["focus_vector"])


class TestNode15ElevenLabs(unittest.TestCase):
    """Verifies Node 15 ElevenLabs audio synthesis and fallback audio generation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.audio_engine = ElevenLabsAudioEngine()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_fallback_audio_generation(self):
        out_wav = os.path.join(self.temp_dir, "test_audio.wav")
        success = self.audio_engine.synthesize_voiceover(
            input_text="Welcome to the Goings OS media synthesis engine.",
            target_output_path=out_wav
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_wav))
        self.assertGreater(os.path.getsize(out_wav), 1000)

        # Validate WAV RIFF header
        with open(out_wav, "rb") as f:
            header = f.read(12)
            self.assertEqual(header[:4], b"RIFF")
            self.assertEqual(header[8:12], b"WAVE")

    def test_convenience_helper(self):
        out_wav = os.path.join(self.temp_dir, "test_helper.wav")
        success = synthesize_voiceover("Testing convenience helper audio output.", out_wav)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_wav))


class TestVideoProductionEngine(unittest.TestCase):
    """Verifies Node 16 Media VideoProductionEngine pipeline."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, "test_vault.db")
        self.engine = VideoProductionEngine(
            base_dir=self.temp_dir,
            vault_bucket="test-vault-bucket",
            db_path=self.temp_db
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mp4_container_structure(self):
        raw_data = b"Sample video stream data content"
        container = generate_mp4_container_bytes(raw_data)
        # Check ftyp box
        self.assertIn(b"ftypmp42", container[:16])
        # Check mdat box
        self.assertIn(b"mdat", container)
        # Check moov box
        self.assertIn(b"moov", container)

    def test_render_storyboard_card(self):
        card_path = os.path.join(self.temp_dir, "test_card.png")
        result = self.engine.render_storyboard_card(
            scene_title="Scene 1: Introduction",
            scene_text="High resolution tracking shot across the waterfront venue.",
            entity_name="Luxury Affairs Event Center",
            output_image_path=card_path,
            dimensions=(1280, 720)
        )
        self.assertEqual(result, card_path)
        self.assertTrue(os.path.exists(card_path))

        with Image.open(card_path) as img:
            self.assertEqual(img.size, (1280, 720))
            self.assertEqual(img.format, "PNG")

    def test_assemble_video(self):
        dummy_audio = os.path.join(self.temp_dir, "dummy_audio.wav")
        with open(dummy_audio, "wb") as f:
            f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

        metadata = {
            "campaign_id": "TEST_CAMP_01",
            "target_entity": "Keep It Goings LLC",
            "storyboard_sequence": (
                "Scene 1: Introduction to architecture. "
                "Scene 2: Multi-tenant database security. "
                "Scene 3: Complete operational compliance."
            )
        }
        out_video = os.path.join(self.temp_dir, "test_video.mp4")
        manifest = self.engine.assemble_video(metadata, dummy_audio, out_video)

        self.assertTrue(os.path.exists(out_video))
        self.assertGreater(os.path.getsize(out_video), 100)
        self.assertEqual(manifest["campaign_id"], "TEST_CAMP_01")
        self.assertEqual(manifest["target_entity"], "Keep It Goings LLC")
        self.assertEqual(manifest["scene_count"], 3)
        self.assertTrue(os.path.exists(manifest["poster_path"]))
        self.assertTrue(os.path.exists(manifest["manifest_path"]))
        self.assertTrue(len(manifest["sha256_checksum"]) == 64)

    def test_persist_to_gcs_vault_fallback(self):
        # When storage_client is None, fallback stores to local mirror
        dummy_video = os.path.join(self.temp_dir, "test_out.mp4")
        with open(dummy_video, "wb") as f:
            f.write(b"DUMMY_MP4_BYTES")

        meta = {"campaign_id": "CAMP_FALLBACK"}
        vault_res = self.engine.persist_to_gcs_vault(dummy_video, meta)

        self.assertEqual(vault_res["bucket"], "test-vault-bucket")
        self.assertEqual(vault_res["gcs_uri"], "gs://test-vault-bucket/rendered_videos/CAMP_FALLBACK/test_out.mp4")
        self.assertEqual(vault_res["persisted_storage"], "LOCAL_VAULT_MIRROR")
        self.assertTrue(os.path.exists(vault_res["local_mirror_path"]))

    def test_persist_to_gcs_vault_with_mock_client(self):
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        self.engine.storage_client = mock_storage
        dummy_video = os.path.join(self.temp_dir, "test_mock.mp4")
        with open(dummy_video, "wb") as f:
            f.write(b"MOCK_MP4_BYTES")

        meta = {"campaign_id": "CAMP_MOCK", "poster_path": None, "manifest_path": None}
        vault_res = self.engine.persist_to_gcs_vault(dummy_video, meta)

        mock_storage.bucket.assert_called_with("test-vault-bucket")
        mock_bucket.blob.assert_called_with("rendered_videos/CAMP_MOCK/test_mock.mp4")
        mock_blob.upload_from_filename.assert_called_once()
        self.assertEqual(vault_res["persisted_storage"], "GCS_LIVE_VERIFIED")

    def test_log_vault_telemetry(self):
        self.engine.log_vault_telemetry(
            campaign_id="CAMP_LOG_01",
            entity_name="Luxury Affairs Event Center",
            video_uri="gs://test-vault-bucket/rendered_videos/CAMP_LOG_01/master.mp4",
            status="SUCCESS_PRODUCED"
        )
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT campaign_id, entity_name, execution_status FROM media_video_production_runs")
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "CAMP_LOG_01")
        self.assertEqual(row[1], "Luxury Affairs Event Center")
        self.assertEqual(row[2], "SUCCESS_PRODUCED")

    def test_execute_production_run_end_to_end(self):
        result = self.engine.execute_production_run(
            entity_name="Norfolk Takeover Cruise LLC",
            campaign_id="E2E_NTC_TEST"
        )
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["campaign_id"], "E2E_NTC_TEST")
        self.assertEqual(result["entity_name"], "Norfolk Takeover Cruise LLC")
        self.assertIn("assembly", result)
        self.assertIn("vault", result)
        self.assertTrue(os.path.exists(result["assembly"]["output_video_path"]))
        self.assertTrue(os.path.exists(result["assembly"]["poster_path"]))


class TestMCPGatewayIntegrity(unittest.TestCase):
    """Ensures mounting VideoProductionEngine causes zero regression to the active MCP Gateway."""

    def test_ingress_gateway_routes(self):
        import ingress_gateway
        routes = [route.path for route in ingress_gateway.app.routes]
        self.assertIn("/mcp", routes)
        self.assertIn("/health", routes)
        self.assertIn("/credit", routes)
        self.assertIn("/spotlight", routes)


if __name__ == "__main__":
    unittest.main()
