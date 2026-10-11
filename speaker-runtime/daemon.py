"""
Speaker Runtime Daemon (Iraqi AI Smart Speaker)
Provides background control, state synchronization, audio streaming,
and RGB animation server on port 8443.
"""

import os
import sys
import json
import time
import socket
import threading
from typing import Dict, Any

# Ensure import from sibling modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared_protocol.protocol import SpeakerConfig, ProtocolFrame
from firmware_adapters.ingenic_x1800_adapter import IngenicX1800Adapter

class SpeakerRuntimeDaemon:
    def __init__(self, host: str = "0.0.0.0", port: int = 8443, is_native: bool = False):
        self.host = host
        self.port = port
        self.adapter = IngenicX1800Adapter(is_native=is_native)
        self.config = SpeakerConfig()
        self.current_state = "IDLE"  # OFFLINE, IDLE, LISTENING, THINKING, SPEAKING, MUSIC, ERROR
        self.is_running = False
        self.server_socket = None

    def start(self):
        self.is_running = True
        self.adapter.set_rgb("#00DCFF", mode="solid", brightness=120)
        self.current_state = "IDLE"
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[+] Speaker Runtime Daemon running on {self.host}:{self.port}")
        
        server_thread = threading.Thread(target=self._accept_clients, daemon=True)
        server_thread.start()

    def _accept_clients(self):
        while self.is_running:
            try:
                client_sock, addr = self.server_socket.accept()
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, client_sock):
        buffer = ""
        try:
            while self.is_running:
                data = client_sock.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        response = self._process_command(line.strip())
                        client_sock.sendall((response + "\n").encode("utf-8"))
        finally:
            client_sock.close()

    def _process_command(self, raw_msg: str) -> str:
        try:
            frame = ProtocolFrame.unpack(raw_msg)
            ftype = frame.get("type")
            payload = frame.get("payload", {})
            
            if ftype == ProtocolFrame.FRAME_CONFIG_SYNC_REQ:
                # Synchronize configuration
                new_cfg = SpeakerConfig.from_json(json.dumps(payload))
                if new_cfg.verify_checksum():
                    self.config = new_cfg
                    self.config.sync_status = "SAVED_ON_SPEAKER"
                    # Apply RGB settings immediately
                    if self.config.rgb_enabled:
                        self.adapter.set_rgb(self.config.rgb_color, mode=self.config.rgb_mode, brightness=self.config.rgb_brightness)
                    return ProtocolFrame.pack(ProtocolFrame.FRAME_CONFIG_SYNC_ACK, {"status": "SUCCESS", "config": self.config.to_dict()})
                else:
                    return ProtocolFrame.pack(ProtocolFrame.FRAME_CONFIG_SYNC_ACK, {"status": "CHECKSUM_MISMATCH"})

            elif ftype == "GET_STATE":
                state_data = {
                    "state": self.current_state,
                    "model_id": self.config.model_id,
                    "character_name": self.config.character_name,
                    "dialect": self.config.dialect,
                    "volume": self.config.music_preferences.get("default_volume", 80),
                    "bluetooth_mode": self.config.bluetooth_mode,
                    "rgb_color": self.config.rgb_color
                }
                return ProtocolFrame.pack("STATE_RESP", state_data)

            elif ftype == "SET_RGB":
                color = payload.get("color", "#00DCFF")
                mode = payload.get("mode", "solid")
                brightness = payload.get("brightness", 200)
                self.adapter.set_rgb(color, mode, brightness)
                return ProtocolFrame.pack("ACK", {"msg": "RGB updated"})

            elif ftype == "SET_VOLUME":
                level = payload.get("volume", 80)
                self.adapter.set_volume(level)
                return ProtocolFrame.pack("ACK", {"msg": f"Volume set to {level}%"})

            elif ftype == "SET_BT_MODE":
                enable = payload.get("enable", False)
                self.adapter.set_bluetooth_speaker_mode(enable)
                self.config.bluetooth_mode = "A2DP_SPEAKER" if enable else "AI_ASSISTANT"
                return ProtocolFrame.pack("ACK", {"msg": f"Bluetooth mode: {self.config.bluetooth_mode}"})

            else:
                return ProtocolFrame.pack("ERROR", {"msg": f"Unknown frame: {ftype}"})

        except Exception as e:
            return ProtocolFrame.pack("ERROR", {"msg": str(e)})

    def stop(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        self.adapter.set_rgb("#000000", mode="off")

if __name__ == "__main__":
    daemon = SpeakerRuntimeDaemon()
    daemon.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daemon.stop()
