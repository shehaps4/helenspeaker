package com.iraqi.smart.speaker.connectivity

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothSocket
import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.Inet4Address
import java.net.InetSocketAddress
import java.net.NetworkInterface
import java.net.Socket
import java.util.UUID

data class SpeakerDiscoveryResult(
    val ip: String,
    val isPairingMode: Boolean,
    val speakerName: String,
    val mode: String,
    val connectionType: String = "Wi-Fi"
)

class SpeakerBridgeClient(
    var host: String = "192.168.1.1",
    val port: Int = 8443
) {
    private var btSocket: BluetoothSocket? = null
    private val sppUuid: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

    fun updateHost(newHost: String) {
        if (newHost.isNotBlank()) {
            host = newHost.trim()
        }
    }

    private fun getActiveSubnets(): List<String> {
        val subnets = mutableListOf<String>()
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val iface = interfaces.nextElement()
                if (iface.isLoopback || !iface.isUp) continue
                val addrs = iface.inetAddresses
                while (addrs.hasMoreElements()) {
                    val addr = addrs.nextElement()
                    if (addr is Inet4Address && !addr.isLoopbackAddress) {
                        val ip = addr.hostAddress ?: ""
                        val lastDot = ip.lastIndexOf('.')
                        if (lastDot > 0) {
                            subnets.add(ip.substring(0, lastDot + 1))
                        }
                    }
                }
            }
        } catch (_: Exception) {}

        // Add common fallback subnets
        val fallbacks = listOf("192.168.1.", "192.168.0.", "192.168.43.", "192.168.8.", "192.168.100.")
        for (fb in fallbacks) {
            if (!subnets.contains(fb)) subnets.add(fb)
        }
        return subnets.distinct()
    }

    private fun probeSocket(ip: String, timeoutMs: Int = 1200): SpeakerDiscoveryResult? {
        return try {
            Socket().use { socket ->
                socket.connect(InetSocketAddress(ip, port), timeoutMs)
                socket.soTimeout = 2000
                val writer = OutputStreamWriter(socket.getOutputStream(), Charsets.UTF_8)
                val reader = BufferedReader(InputStreamReader(socket.getInputStream(), Charsets.UTF_8))
                writer.write("DISCOVER\n")
                writer.flush()
                val resp = reader.readLine()
                if (resp != null && (resp.contains("SMAATI_SPEAKER_OK") || resp.contains("IRAQI_OS_STATUS"))) {
                    val isPairing = resp.contains("PAIRING=YES") || resp.contains("Pairing=YES")
                    val mode = if (resp.contains("MODE=BT") || resp.contains("Mode=BT")) "BT" else "AI"
                    SpeakerDiscoveryResult(
                        ip = ip,
                        isPairingMode = isPairing,
                        speakerName = "سماعتي الذكية",
                        mode = mode,
                        connectionType = if (ip == "192.168.1.1") "نقطة اتصال السماعة (Smaati_Setup)" else "Wi-Fi LAN"
                    )
                } else null
            }
        } catch (_: Exception) {
            null
        }
    }

    suspend fun discoverSpeakerOnLan(): SpeakerDiscoveryResult? = withContext(Dispatchers.IO) {
        // Priority 1: Check speaker's direct Hotspot IP (192.168.1.1) and current host
        val priorityIps = listOf("192.168.1.1", host).filter { it.isNotBlank() && it != "127.0.0.1" }.distinct()
        for (ip in priorityIps) {
            val direct = probeSocket(ip, timeoutMs = 1500)
            if (direct != null) {
                host = direct.ip
                return@withContext direct
            }
        }

        // Priority 2: Check standard localhost / emulator ports
        for (ip in listOf("10.0.2.2", "127.0.0.1")) {
            val local = probeSocket(ip, timeoutMs = 800)
            if (local != null) {
                host = local.ip
                return@withContext local
            }
        }

        // Priority 3: Scan active subnet IPs
        val candidateIps = mutableListOf<String>()
        val activeSubnets = getActiveSubnets()
        for (sub in activeSubnets) {
            for (i in 1..40) {
                candidateIps.add("$sub$i")
            }
        }

        val deferredResults = candidateIps.distinct().map { ip ->
            async {
                probeSocket(ip, timeoutMs = 500)
            }
        }

        val found = deferredResults.awaitAll().filterNotNull().firstOrNull()
        if (found != null) {
            host = found.ip
        }
        found
    }

    suspend fun connectBluetooth(): Boolean = withContext(Dispatchers.IO) {
        try {
            val adapter = BluetoothAdapter.getDefaultAdapter() ?: return@withContext false
            if (!adapter.isEnabled) return@withContext false

            val bonded = try { adapter.bondedDevices } catch (_: SecurityException) { null } ?: emptySet()
            val target = bonded.firstOrNull {
                val n = it.name ?: ""
                n.contains("Smaati", ignoreCase = true) ||
                n.contains("سماعتي", ignoreCase = true) ||
                it.address.equals("70:4F:08:00:84:C8", ignoreCase = true)
            } ?: return@withContext false

            try { btSocket?.close() } catch (_: Exception) {}
            val socket = target.createRfcommSocketToServiceRecord(sppUuid)
            socket.connect()
            btSocket = socket
            true
        } catch (_: Exception) {
            false
        }
    }

    suspend fun isBluetoothConnected(): Boolean = withContext(Dispatchers.IO) {
        btSocket?.isConnected == true
    }

    suspend fun sendRawCommand(cmd: String): String = withContext(Dispatchers.IO) {
        // Build targets with speaker AP IP first if not configured
        val targets = mutableListOf<String>()
        if (host.isNotBlank() && host != "127.0.0.1") targets.add(host)
        targets.add("192.168.1.1") // Direct Hotspot Gateway
        targets.add("10.0.2.2")   // Emulator bridge
        targets.add("127.0.0.1")  // ADB forward fallback

        for (target in targets.distinct()) {
            try {
                Socket().use { socket ->
                    socket.connect(InetSocketAddress(target, port), 2000)
                    socket.soTimeout = 3500
                    val writer = OutputStreamWriter(socket.getOutputStream(), Charsets.UTF_8)
                    val reader = BufferedReader(InputStreamReader(socket.getInputStream(), Charsets.UTF_8))

                    writer.write("$cmd\n")
                    writer.flush()
                    val resp = reader.readLine()
                    if (resp != null) {
                        host = target
                        return@withContext resp
                    }
                }
            } catch (_: Exception) {}
        }

        // Fallback: If Wi-Fi socket failed, try Bluetooth SPP if available
        if (btSocket?.isConnected == true) {
            try {
                val socket = btSocket!!
                val os = socket.outputStream
                val isr = BufferedReader(InputStreamReader(socket.inputStream, Charsets.UTF_8))
                os.write("$cmd\n".toByteArray(Charsets.UTF_8))
                os.flush()
                val resp = isr.readLine()
                if (resp != null) return@withContext resp
            } catch (_: Exception) {}
        }

        "ERR-CONNECT"
    }

    suspend fun setVolume(volume: Int): Boolean = withContext(Dispatchers.IO) {
        val alsaLevel = (volume * 31 / 100).coerceIn(0, 31)
        val resp = sendRawCommand("VOL $alsaLevel")
        resp.contains("VOLUME_SET")
    }

    suspend fun setRgb(colorHex: String, mode: String = "solid", brightness: Int = 200): Boolean = withContext(Dispatchers.IO) {
        val ledState = when (mode.lowercase()) {
            "listening", "talk" -> "LISTENING"
            "thinking" -> "THINKING"
            "speaking" -> "SPEAKING"
            "romance" -> "ROMANCE"
            "bt", "bluetooth" -> "BT_MODE"
            else -> "IDLE"
        }
        val resp = sendRawCommand("LED_STATE $ledState")
        resp.contains("LED_STATE")
    }

    suspend fun setBluetoothMode(enabled: Boolean): Boolean = withContext(Dispatchers.IO) {
        val cmd = if (enabled) "BT_ENABLE" else "BT_DISABLE"
        val resp = sendRawCommand(cmd)
        resp.contains("ACTIVE")
    }

    suspend fun playTrack(target: String): Boolean = withContext(Dispatchers.IO) {
        val resp = sendRawCommand("PLAY $target")
        resp.contains("PLAYING")
    }

    suspend fun stopTrack(): Boolean = withContext(Dispatchers.IO) {
        val resp = sendRawCommand("STOP")
        resp.contains("STOPPED")
    }

    suspend fun getSpeakerStatus(): String = withContext(Dispatchers.IO) {
        sendRawCommand("STATUS")
    }

    suspend fun setWifi(ssid: String, psk: String): String = withContext(Dispatchers.IO) {
        sendRawCommand("SET_WIFI $ssid $psk")
    }
}
