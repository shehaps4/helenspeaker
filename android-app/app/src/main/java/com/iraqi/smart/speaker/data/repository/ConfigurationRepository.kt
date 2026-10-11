package com.iraqi.smart.speaker.data.repository

import com.google.gson.Gson
import com.iraqi.smart.speaker.data.model.SpeakerConfig
import com.iraqi.smart.speaker.data.model.SyncStatus
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.InetSocketAddress
import java.net.Socket

class ConfigurationRepository {

    private val gson = Gson()
    private val _configFlow = MutableStateFlow(
        SpeakerConfig().let { it.copy(checksum = it.calculateChecksum()) }
    )
    val configFlow: StateFlow<SpeakerConfig> = _configFlow.asStateFlow()

    fun updateConfig(update: (SpeakerConfig) -> SpeakerConfig) {
        val current = _configFlow.value
        val modified = update(current)
        val withChecksum = modified.copy(
            checksum = modified.calculateChecksum(),
            syncStatus = SyncStatus.PENDING_SYNC
        )
        _configFlow.value = withChecksum
    }

    suspend fun sendCommandToSpeaker(cmd: String): String = withContext(Dispatchers.IO) {
        val current = _configFlow.value
        val ipsToTry = mutableListOf<String>()
        if (current.speakerIp.isNotBlank() && current.speakerIp != "127.0.0.1") {
            ipsToTry.add(current.speakerIp)
        }
        ipsToTry.add("192.168.1.1")
        ipsToTry.add("10.0.2.2")
        ipsToTry.add("127.0.0.1")
        var lastErr = ""

        for (ip in ipsToTry.distinct()) {
            try {
                Socket().use { socket ->
                    socket.connect(InetSocketAddress(ip, current.speakerPort), 2000)
                    socket.soTimeout = 3500
                    val writer = OutputStreamWriter(socket.getOutputStream(), Charsets.UTF_8)
                    val reader = BufferedReader(InputStreamReader(socket.getInputStream(), Charsets.UTF_8))

                    writer.write("$cmd\n")
                    writer.flush()

                    val response = reader.readLine() ?: ""
                    if (current.speakerIp != ip) {
                        _configFlow.value = _configFlow.value.copy(speakerIp = ip)
                    }
                    return@withContext response
                }
            } catch (e: Exception) {
                lastErr = e.message ?: "Connection error"
            }
        }
        throw Exception("Failed to connect to speaker at port ${current.speakerPort}: $lastErr")
    }

    suspend fun syncWithSpeaker(): SyncStatus = withContext(Dispatchers.IO) {
        val current = _configFlow.value
        try {
            val jsonPayload = gson.toJson(current)
            val resp = sendCommandToSpeaker("SET_CONFIG $jsonPayload")
            
            if (current.wifiSsid.isNotBlank()) {
                sendCommandToSpeaker("SET_WIFI ${current.wifiSsid} ${current.wifiPassword}")
            }

            if (resp.contains("CONFIG_SAVED_OK") || resp.isNotBlank()) {
                val synced = current.copy(syncStatus = SyncStatus.SAVED_ON_SPEAKER)
                _configFlow.value = synced
                SyncStatus.SAVED_ON_SPEAKER
            } else {
                _configFlow.value = current.copy(syncStatus = SyncStatus.SYNC_FAILED)
                SyncStatus.SYNC_FAILED
            }
        } catch (e: Exception) {
            // If network socket is unreachable (e.g. phone running without adb port forward yet),
            // retain local state and flag
            _configFlow.value = current.copy(syncStatus = SyncStatus.SAVED_LOCAL_PHONE)
            SyncStatus.SAVED_LOCAL_PHONE
        }
    }

    suspend fun setRgbState(state: String) {
        try {
            sendCommandToSpeaker("LED_STATE $state")
        } catch (_: Exception) {}
    }

    suspend fun setSpeakerVolume(volume: Int) {
        try {
            sendCommandToSpeaker("VOL $volume")
        } catch (_: Exception) {}
    }

    suspend fun toggleBluetoothMode(enable: Boolean) {
        try {
            if (enable) {
                sendCommandToSpeaker("BT_ENABLE")
            } else {
                sendCommandToSpeaker("BT_DISABLE")
            }
        } catch (_: Exception) {}
    }
}
