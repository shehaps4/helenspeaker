package com.iraqi.smart.speaker.data.model

import com.google.gson.annotations.SerializedName
import java.security.MessageDigest

enum class SyncStatus {
    SAVED_LOCAL_PHONE,
    PENDING_SYNC,
    SAVED_ON_SPEAKER,
    SYNC_FAILED,
    NOT_SUPPORTED
}

data class SpeakerConfig(
    @SerializedName("configuration_version") val version: Int = 2,
    @SerializedName("speaker_id") val speakerId: String = "audio_84c8",
    @SerializedName("api_key") val apiKey: String = "",
    @SerializedName("live_model") val liveModel: String = "gemini-2.0-flash-exp",
    @SerializedName("character_name") val characterName: String = "ريام",
    @SerializedName("dialect") val dialect: String = "baghdadi",
    @SerializedName("voice_gender") val voiceGender: String = "female",
    @SerializedName("voice_name") val voiceName: String = "Kore",
    @SerializedName("relationship_style") val relationshipStyle: String = "Romantic",
    @SerializedName("romance_level") val romanceLevel: Int = 90,
    @SerializedName("boldness_level") val boldnessLevel: Int = 85,
    @SerializedName("humor_level") val humorLevel: Int = 85,
    @SerializedName("wifi_ssid") val wifiSsid: String = "",
    @SerializedName("wifi_password") val wifiPassword: String = "",
    @SerializedName("rgb_enabled") val rgbEnabled: Boolean = true,
    @SerializedName("rgb_mode") val rgbMode: String = "LISTENING",
    @SerializedName("rgb_color") val rgbColor: String = "#00DCFF",
    @SerializedName("rgb_brightness") val rgbBrightness: Int = 200,
    @SerializedName("bluetooth_mode") val bluetoothMode: String = "AI_ASSISTANT",
    @SerializedName("speaker_ip") val speakerIp: String = "127.0.0.1",
    @SerializedName("speaker_port") val speakerPort: Int = 8443,
    @SerializedName("sync_status") val syncStatus: SyncStatus = SyncStatus.SAVED_LOCAL_PHONE,
    @SerializedName("checksum") val checksum: String = ""
) {
    fun calculateChecksum(): String {
        val payload = "$version|$speakerId|$apiKey|$characterName|$voiceGender|$voiceName|$dialect|$relationshipStyle|$romanceLevel|$boldnessLevel|$humorLevel|$rgbColor|$bluetoothMode"
        val bytes = MessageDigest.getInstance("SHA-256").digest(payload.toByteArray(Charsets.UTF_8))
        return bytes.joinToString("") { "%02x".format(it) }
    }

    fun isChecksumValid(): Boolean = checksum == calculateChecksum()
}

data class DeviceTelemetry(
    val speakerId: String = "audio_84c8",
    val boardModel: String = "audio_ihuisen_shanyuan_V2_0",
    val soc: String = "Ingenic XBurst MIPS (X1800/X1830 @ 1.36 GHz)",
    val ram: String = "64 MB DDR (55 MB Usable)",
    val flashFree: String = "21.9 MB Userdata Persistent RW",
    val isConnected: Boolean = true,
    val isMicActive: Boolean = false,
    val isAiSpeaking: Boolean = false,
    val currentVolume: Int = 85,
    val speakerMode: String = "AI_ASSISTANT",
    val activeModel: String = "Gemini 2.0 Flash Realtime (Live Audio-to-Audio)",
    val connectionType: String = "Wi-Fi + ADB Bridge (Port 8443)"
)
