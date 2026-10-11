"""
Shared Protocol and Configuration Repository Library
Used by Android App, Backend, and Speaker Runtime.
Provides robust serialization, validation, and SHA-256 checksums.
"""

import json
import hashlib
from typing import Dict, Any, Optional

class ProtocolError(Exception):
    pass

class SpeakerConfig:
    def __init__(
        self,
        speaker_id: str = "audio_84c8",
        character_name: str = "هيلين",
        dialect: str = "baghdadi",
        voice_id: str = "ar-IQ-RanaNeural",
        model_id: str = "gemini-3.8-live",
        relationship_style: str = "playful_lover",
        romance_level: int = 75,
        playfulness_level: int = 85,
        humor_level: int = 80,
        warmth_level: int = 90,
        boldness_level: int = 65,
        rgb_enabled: bool = True,
        rgb_mode: str = "idle",
        rgb_color: str = "#00DCFF",
        rgb_brightness: int = 200,
        music_preferences: Optional[Dict[str, Any]] = None,
        wake_word_settings: Optional[Dict[str, Any]] = None,
        bluetooth_mode: str = "AI_ASSISTANT",
        wifi_profile_reference: str = "secure_keystore_ref",
        configuration_version: int = 1,
        sync_status: str = "SAVED_LOCAL_PHONE",
        checksum: str = ""
    ):
        self.speaker_id = speaker_id
        self.character_name = character_name
        self.dialect = dialect
        self.voice_id = voice_id
        self.model_id = model_id
        self.relationship_style = relationship_style
        self.romance_level = romance_level
        self.playfulness_level = playfulness_level
        self.humor_level = humor_level
        self.warmth_level = warmth_level
        self.boldness_level = boldness_level
        self.rgb_enabled = rgb_enabled
        self.rgb_mode = rgb_mode
        self.rgb_color = rgb_color
        self.rgb_brightness = rgb_brightness
        self.music_preferences = music_preferences or {"favorite_genre": "Iraqi Classic", "default_volume": 80}
        self.wake_word_settings = wake_word_settings or {"enabled": True, "wake_word": "يا هيلين", "sensitivity": 0.5}
        self.bluetooth_mode = bluetooth_mode
        self.wifi_profile_reference = wifi_profile_reference
        self.configuration_version = configuration_version
        self.sync_status = sync_status
        self.checksum = checksum or self.calculate_checksum()

    def to_dict(self, include_checksum: bool = True) -> Dict[str, Any]:
        data = {
            "configuration_version": self.configuration_version,
            "speaker_id": self.speaker_id,
            "character_name": self.character_name,
            "dialect": self.dialect,
            "voice_id": self.voice_id,
            "model_id": self.model_id,
            "relationship_style": self.relationship_style,
            "romance_level": self.romance_level,
            "playfulness_level": self.playfulness_level,
            "humor_level": self.humor_level,
            "warmth_level": self.warmth_level,
            "boldness_level": self.boldness_level,
            "rgb_enabled": self.rgb_enabled,
            "rgb_mode": self.rgb_mode,
            "rgb_color": self.rgb_color,
            "rgb_brightness": self.rgb_brightness,
            "music_preferences": self.music_preferences,
            "wake_word_settings": self.wake_word_settings,
            "bluetooth_mode": self.bluetooth_mode,
            "wifi_profile_reference": self.wifi_profile_reference,
            "sync_status": self.sync_status
        }
        if include_checksum:
            data["checksum"] = self.checksum or self.calculate_checksum()
        return data

    def calculate_checksum(self) -> str:
        # Create canonical representation excluding checksum & sync_status
        d = self.to_dict(include_checksum=False)
        d.pop("sync_status", None)
        canonical_str = json.dumps(d, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def verify_checksum(self) -> bool:
        return self.checksum == self.calculate_checksum()

    @classmethod
    def from_json(cls, json_str: str) -> "SpeakerConfig":
        d = json.loads(json_str)
        return cls(**d)

    def to_json(self) -> str:
        self.checksum = self.calculate_checksum()
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class ProtocolFrame:
    """Standard binary/JSON framing for over-the-air communication."""
    
    FRAME_CONFIG_SYNC_REQ = "CONFIG_SYNC_REQ"
    FRAME_CONFIG_SYNC_ACK = "CONFIG_SYNC_ACK"
    FRAME_STATE_UPDATE = "STATE_UPDATE"
    FRAME_DIAGNOSTIC_REQ = "DIAGNOSTIC_REQ"
    FRAME_DIAGNOSTIC_RESP = "DIAGNOSTIC_RESP"
    FRAME_AUDIO_STREAM_CTRL = "AUDIO_STREAM_CTRL"
    FRAME_TOOL_CALL = "TOOL_CALL"
    FRAME_TOOL_RESULT = "TOOL_RESULT"

    @staticmethod
    def pack(frame_type: str, payload: Dict[str, Any]) -> str:
        frame = {
            "type": frame_type,
            "timestamp": hashlib.sha256(str(payload).encode("utf-8")).hexdigest()[:8],
            "payload": payload
        }
        return json.dumps(frame, ensure_ascii=False)

    @staticmethod
    def unpack(raw_data: str) -> Dict[str, Any]:
        try:
            return json.loads(raw_data)
        except json.JSONDecodeError as e:
            raise ProtocolError(f"Corrupted frame JSON: {e}")
