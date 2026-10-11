import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "shared-protocol")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from protocol import SpeakerConfig
from backend.iraqi_persona_engine import IraqiPersonaEngine

class TestIraqiPersona(unittest.TestCase):
    def test_baghdadi_prompt_generation(self):
        cfg = SpeakerConfig(
            character_name="هيلين",
            dialect="baghdadi",
            relationship_style="playful_lover",
            romance_level=80,
            playfulness_level=90
        )
        prompt = IraqiPersonaEngine.build_system_prompt(cfg)
        self.assertIn("هيلين", prompt)
        self.assertIn("اللهجة البغدادية الأصيلة", prompt)
        self.assertIn("فدوه لعينك", prompt)
        self.assertIn("80/100", prompt)

    def test_southern_prompt_generation(self):
        cfg = SpeakerConfig(
            character_name="شهد",
            dialect="southern_iq",
            relationship_style="close_friend"
        )
        prompt = IraqiPersonaEngine.build_system_prompt(cfg)
        self.assertIn("شهد", prompt)
        self.assertIn("اللهجة الجنوبية العراقية", prompt)
        self.assertIn("يابعد روحي", prompt)

if __name__ == "__main__":
    unittest.main()
