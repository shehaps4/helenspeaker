import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "firmware-adapters")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.assistant_tools import AssistantToolRegistry
from ingenic_x1800_adapter import IngenicX1800Adapter

class TestToolsAndHardware(unittest.TestCase):
    def test_tool_registry_execution(self):
        registry = AssistantToolRegistry()
        res = registry.execute_tool("play_music", {"action": "play", "track_name": "حلو حبك"})
        self.assertEqual(res["status"], "success")
        self.assertIn("حلو حبك", res["data"])

    def test_invalid_tool(self):
        registry = AssistantToolRegistry()
        res = registry.execute_tool("unknown_command", {})
        self.assertEqual(res["status"], "error")

    def test_hex_to_rgb_conversion(self):
        r, g, b = IngenicX1800Adapter.hex_to_rgb("#00DCFF")
        self.assertEqual(r, 0)
        self.assertEqual(g, 220)
        self.assertEqual(b, 255)

        r, g, b = IngenicX1800Adapter.hex_to_rgb("#FF0000")
        self.assertEqual(r, 255)
        self.assertEqual(g, 0)
        self.assertEqual(b, 0)

if __name__ == "__main__":
    unittest.main()
