"""
Ingenic XBurst X1800 / X1830 Hardware Abstraction Adapter
Interacts directly with AW2015 RGB driver, Mic DMA, ALSA Codec, and BlueZ.
Works both natively inside the MIPS Linux speaker and remotely via ADB bridge.
"""

import os
import subprocess
import time
from typing import Tuple

class IngenicX1800Adapter:
    def __init__(self, serial: str = "audio_84c8", is_native: bool = False):
        self.serial = serial
        self.is_native = is_native
        self.adb_path = os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe")
        if not os.path.exists(self.adb_path):
            self.adb_path = "adb"

    def execute_sh(self, cmd: str) -> str:
        """Run command either natively or via ADB shell."""
        if self.is_native:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.stdout.strip()
        else:
            full_cmd = f'"{self.adb_path}" -s {self.serial} shell "{cmd}"'
            res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
            return res.stdout.strip()

    # ==================== RGB LED CONTROL (AW2015) ====================
    @staticmethod
    def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
        h = hex_code.lstrip("#")
        if len(h) != 6:
            return (0, 220, 255)
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def set_rgb(self, color_hex: str, mode: str = "solid", brightness: int = 200):
        r, g, b = self.hex_to_rgb(color_hex)
        # Scale with brightness
        scale = brightness / 255.0
        r_sc = int(r * scale)
        g_sc = int(g * scale)
        b_sc = int(b * scale)

        if mode == "off":
            self.execute_sh("echo 'r 0 g 0 b 0' > /sys/class/leds/aw2015/color_blink; echo 'r 0 g 0 b 0' > /sys/class/leds/aw2015/color_brightness")
        elif mode == "pulse":
            self.execute_sh(f"echo 'r {r_sc} g {g_sc} b {b_sc}' > /sys/class/leds/aw2015/color_blink")
        elif mode == "solid":
            self.execute_sh("echo 'r 0 g 0 b 0' > /sys/class/leds/aw2015/color_blink")
            self.execute_sh(f"echo 'r {r_sc} g {g_sc} b {b_sc}' > /sys/class/leds/aw2015/color_brightness")
        elif mode == "listening":
            self.execute_sh("echo 'r 0 g 220 b 255' > /sys/class/leds/aw2015/color_blink")
        elif mode == "thinking":
            self.execute_sh("echo 'r 255 g 160 b 0' > /sys/class/leds/aw2015/color_brightness")
        elif mode == "speaking":
            self.execute_sh("echo 'r 0 g 255 b 100' > /sys/class/leds/aw2015/color_blink")
        elif mode == "error":
            self.execute_sh("echo 'r 255 g 0 b 0' > /sys/class/leds/aw2015/color_blink")

    # ==================== AUDIO VOLUME & PLAYBACK ====================
    def set_volume(self, percentage: int):
        """Map 0-100% to ALSA Master limits (0 to 31)."""
        alsa_val = int(max(0, min(100, percentage)) * 31 / 100)
        self.execute_sh(f"amixer sset Master {alsa_val}")

    def play_audio(self, remote_file_path: str, volume: int = 100):
        self.execute_sh(f"mplayer -volume {volume} {remote_file_path} >/dev/null 2>&1 &")

    def stop_audio(self):
        self.execute_sh("killall -9 mplayer 2>/dev/null")

    # ==================== MICROPHONE DMA RECORDING ====================
    def record_mic(self, output_remote_wav: str, duration: int = 5):
        self.execute_sh(f"rm -f {output_remote_wav}; /usr/bin/mic_test -f {output_remote_wav} -d {duration}")

    # ==================== BLUETOOTH SPEAKER MODE ====================
    def set_bluetooth_speaker_mode(self, enable: bool):
        """
        Transition between AI Smart Speaker mode and traditional Bluetooth A2DP Sink mode.
        AI MODE -> STOP AUDIO -> RELEASE MICROPHONE -> ENABLE A2DP SINK
        """
        if enable:
            # Switch to Bluetooth Speaker Mode
            self.stop_audio()
            self.execute_sh("killall -9 mic_test 2>/dev/null")
            self.set_rgb("#0000FF", mode="pulse", brightness=180) # Blue pulse
            self.execute_sh("bluealsa-aplay 00:00:00:00:00:00 >/dev/null 2>&1 &")
        else:
            # Return to AI Smart Speaker mode
            self.execute_sh("killall -9 bluealsa-aplay 2>/dev/null")
            self.set_rgb("#00DCFF", mode="solid", brightness=150)
