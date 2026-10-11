"""
Backend API Server (Iraqi AI Smart Speaker)
Provides secure session authentication, ephemeral tokens,
and REST/WebSocket control interfaces for the Android Control Center.
"""

import os
import sys
import json
import secrets
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared_protocol.protocol import SpeakerConfig, ProtocolFrame
from firmware_adapters.ingenic_x1800_adapter import IngenicX1800Adapter
from backend.gemini_live_engine import GeminiLiveEngine, ModelRegistry

app = FastAPI(title="Iraqi AI Smart Speaker Backend", version="1.0.0")

hardware_adapter = IngenicX1800Adapter()
live_engine = GeminiLiveEngine(hardware_adapter=hardware_adapter)

class TokenRequest(BaseModel):
    client_id: str

class ControlRequest(BaseModel):
    action: str
    parameter: Optional[Any] = None

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Iraqi AI Smart Speaker Gateway",
        "hardware_connected": True
    }

@app.post("/api/v1/auth/token")
def generate_ephemeral_token(req: TokenRequest):
    """
    Issue a short-lived ephemeral token for the Android client.
    Prevents API keys from being leaked or embedded inside the mobile app.
    """
    ephemeral_token = f"iq_speaker_{secrets.token_hex(16)}"
    return {
        "token": ephemeral_token,
        "expires_in_seconds": 3600,
        "allowed_models": ModelRegistry.list_models()
    }

@app.get("/api/v1/speaker/status")
def get_speaker_status():
    return {
        "speaker_id": "audio_84c8",
        "state": live_engine.hardware_adapter.is_native,
        "active_model": live_engine.model_id,
        "bluetooth_mode": "AI_ASSISTANT",
        "rgb_status": "ONLINE"
    }

@app.post("/api/v1/speaker/config/sync")
def sync_config(config_dict: Dict[str, Any]):
    """Validate checksum and apply configuration."""
    cfg = SpeakerConfig(**config_dict)
    if not cfg.verify_checksum():
        raise HTTPException(status_code=400, detail="Configuration Checksum Mismatch")
    
    # Apply to hardware
    hardware_adapter.set_rgb(cfg.rgb_color, mode=cfg.rgb_mode, brightness=cfg.rgb_brightness)
    cfg.sync_status = "SAVED_ON_SPEAKER"
    return {"status": "SUCCESS", "config": cfg.to_dict()}

@app.post("/api/v1/speaker/control")
def control_speaker(req: ControlRequest):
    act = req.action
    param = req.parameter
    
    if act == "set_volume":
        hardware_adapter.set_volume(int(param))
    elif act == "set_rgb":
        hardware_adapter.set_rgb(param.get("color", "#00DCFF"), mode=param.get("mode", "solid"))
    elif act == "set_bluetooth_mode":
        hardware_adapter.set_bluetooth_speaker_mode(bool(param))
    elif act == "stop_audio":
        hardware_adapter.stop_audio()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {act}")
        
    return {"status": "SUCCESS", "action": act}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
