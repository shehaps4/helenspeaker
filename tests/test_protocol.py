import sys
import os
import unittest
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "shared-protocol")))
from protocol import SpeakerConfig, ProtocolFrame

class TestProtocol(unittest.TestCase):
    def test_checksum_calculation_and_verification(self):
        cfg = SpeakerConfig(
            speaker_id="test_speaker_1",
            character_name="هيلين",
            dialect="baghdadi"
        )
        self.assertTrue(cfg.verify_checksum())
        
        # Modify a field without recalculating checksum -> verification must fail
        cfg.character_name = "تغيير غير مصرح به"
        self.assertFalse(cfg.verify_checksum())

    def test_json_roundtrip(self):
        cfg = SpeakerConfig(
            speaker_id="audio_84c8",
            romance_level=90,
            playfulness_level=80
        )
        json_str = cfg.to_json()
        restored = SpeakerConfig.from_json(json_str)
        self.assertEqual(restored.speaker_id, cfg.speaker_id)
        self.assertEqual(restored.romance_level, 90)
        self.assertTrue(restored.verify_checksum())

    def test_protocol_frame_packaging(self):
        frame = ProtocolFrame.pack(ProtocolFrame.FRAME_CONFIG_SYNC_REQ, {"test": 123})
        unpacked = ProtocolFrame.unpack(frame)
        self.assertEqual(unpacked["type"], ProtocolFrame.FRAME_CONFIG_SYNC_REQ)
        self.assertEqual(unpacked["payload"]["test"], 123)

if __name__ == "__main__":
    unittest.main()
