package com.iraqi.smart.speaker

import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.unit.LayoutDirection
import com.iraqi.smart.speaker.connectivity.SpeakerBridgeClient
import com.iraqi.smart.speaker.data.model.DeviceTelemetry
import com.iraqi.smart.speaker.data.repository.ConfigurationRepository
import com.iraqi.smart.speaker.ui.screens.*
import com.iraqi.smart.speaker.ui.theme.BackgroundDark
import com.iraqi.smart.speaker.ui.theme.CyanPrimary
import com.iraqi.smart.speaker.ui.theme.IraqiAiSmartSpeakerTheme
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    private val repository = ConfigurationRepository()
    private val bridgeClient = SpeakerBridgeClient()

    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            IraqiAiSmartSpeakerTheme {
                CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
                    val config by repository.configFlow.collectAsState()
                    var telemetry by remember { mutableStateOf(DeviceTelemetry()) }
                    var selectedTab by remember { mutableStateOf(0) }
                    var isConnected by remember { mutableStateOf(false) }
                    var connectionLabel by remember { mutableStateOf("جاري فحص الاتصال...") }
                    val scope = rememberCoroutineScope()
                    val snackbarHostState = remember { SnackbarHostState() }
                    val context = LocalContext.current

                    // Proactive discovery on launch
                    LaunchedEffect(Unit) {
                        val result = bridgeClient.discoverSpeakerOnLan()
                        if (result != null) {
                            isConnected = true
                            connectionLabel = "متصل: ${result.ip} (${result.connectionType})"
                            repository.updateConfig { it.copy(speakerIp = result.ip) }
                            bridgeClient.updateHost(result.ip)
                        } else {
                            val st = bridgeClient.getSpeakerStatus()
                            if (st != "ERR-CONNECT") {
                                isConnected = true
                                connectionLabel = "متصل (Port 8443)"
                            } else {
                                isConnected = false
                                connectionLabel = "غير متصل - اتبع خطوات الاقتران أدناه"
                            }
                        }
                    }

                    Scaffold(
                        modifier = Modifier.fillMaxSize(),
                        containerColor = BackgroundDark,
                        snackbarHost = { SnackbarHost(snackbarHostState) },
                        topBar = {
                            TopAppBar(
                                title = { Text("سماعتي", fontWeight = androidx.compose.ui.text.font.FontWeight.Bold, color = Color.White) },
                                colors = TopAppBarDefaults.topAppBarColors(containerColor = BackgroundDark),
                                actions = {
                                    IconButton(onClick = {
                                        scope.launch {
                                            snackbarHostState.showSnackbar("جاري البحث عن سماعتي (Wi-Fi / Smaati_Setup)...")
                                            val result = bridgeClient.discoverSpeakerOnLan()
                                            if (result != null) {
                                                isConnected = true
                                                connectionLabel = "متصل: ${result.ip} (${result.connectionType})"
                                                repository.updateConfig { it.copy(speakerIp = result.ip) }
                                                bridgeClient.updateHost(result.ip)
                                                val pairingNote = if (result.isPairingMode) " (جاهزة للاقتران!)" else ""
                                                snackbarHostState.showSnackbar("تم العثور على سماعتي: ${result.ip}$pairingNote")
                                            } else {
                                                val btOk = bridgeClient.connectBluetooth()
                                                if (btOk) {
                                                    isConnected = true
                                                    connectionLabel = "متصل عبر البلوتوث (Smaati_سماعتي)"
                                                    snackbarHostState.showSnackbar("تم الاقتران بنجاح عبر البلوتوث!")
                                                } else {
                                                    val status = bridgeClient.getSpeakerStatus()
                                                    if (status != "ERR-CONNECT") {
                                                        isConnected = true
                                                        connectionLabel = "متصل: $status"
                                                        snackbarHostState.showSnackbar("حالة سماعتي: $status")
                                                    } else {
                                                        isConnected = false
                                                        connectionLabel = "غير متصل"
                                                        snackbarHostState.showSnackbar("لم يتم العثور على السماعة. اتصل بـ Smaati_Setup أولاً.")
                                                    }
                                                }
                                            }
                                        }
                                    }) {
                                        Icon(Icons.Default.WifiFind, contentDescription = "بحث عن سماعتي", tint = CyanPrimary)
                                    }
                                    IconButton(onClick = {
                                        scope.launch {
                                            val status = bridgeClient.getSpeakerStatus()
                                            if (status != "ERR-CONNECT") {
                                                isConnected = true
                                                connectionLabel = "متصل: $status"
                                                snackbarHostState.showSnackbar("استجابة سماعتي: $status")
                                            } else {
                                                isConnected = false
                                                snackbarHostState.showSnackbar("السماعة غير متصلة حالياً")
                                            }
                                        }
                                    }) {
                                        Icon(
                                            if (isConnected) Icons.Default.CheckCircle else Icons.Default.Cancel,
                                            contentDescription = "Status",
                                            tint = if (isConnected) CyanPrimary else Color.Gray
                                        )
                                    }
                                }
                            )
                        },
                        bottomBar = {
                            NavigationBar(containerColor = BackgroundDark) {
                                NavigationBarItem(
                                    selected = selectedTab == 0,
                                    onClick = { selectedTab = 0 },
                                    icon = { Icon(Icons.Default.Home, contentDescription = null) },
                                    label = { Text("الرئيسية") }
                                )
                                NavigationBarItem(
                                    selected = selectedTab == 1,
                                    onClick = { selectedTab = 1 },
                                    icon = { Icon(Icons.Default.Face, contentDescription = null) },
                                    label = { Text("الشخصية") }
                                )
                                NavigationBarItem(
                                    selected = selectedTab == 2,
                                    onClick = { selectedTab = 2 },
                                    icon = { Icon(Icons.Default.Palette, contentDescription = null) },
                                    label = { Text("الإضاءة") }
                                )
                                NavigationBarItem(
                                    selected = selectedTab == 3,
                                    onClick = { selectedTab = 3 },
                                    icon = { Icon(Icons.Default.MusicNote, contentDescription = null) },
                                    label = { Text("الصوتيات") }
                                )
                                NavigationBarItem(
                                    selected = selectedTab == 4,
                                    onClick = { selectedTab = 4 },
                                    icon = { Icon(Icons.Default.Wifi, contentDescription = null) },
                                    label = { Text("الاتصال") }
                                )
                            }
                        }
                    ) { innerPadding ->
                        Surface(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(innerPadding),
                            color = BackgroundDark
                        ) {
                            when (selectedTab) {
                                0 -> DashboardScreen(
                                    config = config,
                                    telemetry = telemetry,
                                    onStartTalk = {
                                        scope.launch {
                                            bridgeClient.setRgb("#00DCFF", "listening", 255)
                                            snackbarHostState.showSnackbar("جاري الاستماع الآن عبر ميكروفون السماعة...")
                                        }
                                    },
                                    onToggleBluetoothMode = { enabled ->
                                        scope.launch {
                                            bridgeClient.setBluetoothMode(enabled)
                                            val msg = if (enabled) "تم تفعيل وضع سماعة البلوتوث" else "تمت العودة لوضع المساعد الذكي"
                                            snackbarHostState.showSnackbar(msg)
                                        }
                                    },
                                    onVolumeChange = { vol ->
                                        scope.launch { bridgeClient.setVolume(vol) }
                                    }
                                )
                                1 -> CharacterStudioScreen(
                                    config = config,
                                    onSaveConfig = { updated ->
                                        scope.launch {
                                            repository.updateConfig { updated }
                                            val syncResult = repository.syncWithSpeaker()
                                            val msg = if (syncResult == com.iraqi.smart.speaker.data.model.SyncStatus.SAVED_ON_SPEAKER)
                                                "تم حفظ جميع الإعدادات داخل نظام السماعة الذكية بنجاح!"
                                            else
                                                "تم حفظ الإعدادات في الهاتف وجاري المزامنة مع السماعة!"
                                            snackbarHostState.showSnackbar(msg)
                                        }
                                    },
                                    onPreviewVoice = { voiceName ->
                                        scope.launch {
                                            snackbarHostState.showSnackbar("معاينة نبرة $voiceName: هلو عيوني شلونك شخبارك!")
                                        }
                                    }
                                )
                                2 -> RgbStudioScreen(
                                    config = config,
                                    onApplyRgb = { color, mode, brightness ->
                                        scope.launch {
                                            bridgeClient.setRgb(color, mode, brightness)
                                            snackbarHostState.showSnackbar("تم تحديث إضاءة AW2015: $mode")
                                        }
                                    }
                                )
                                3 -> MusicAndStoryScreen(
                                    onPlayTrack = { track ->
                                        scope.launch {
                                            bridgeClient.playTrack(track)
                                            snackbarHostState.showSnackbar("تشغيل $track عبر السماعة")
                                        }
                                    },
                                    onStopTrack = {
                                        scope.launch {
                                            bridgeClient.stopTrack()
                                            snackbarHostState.showSnackbar("تم إيقاف التشغيل")
                                        }
                                    },
                                    onStartStory = { story ->
                                        scope.launch {
                                            bridgeClient.setRgb("#FFA000", "speaking", 200)
                                            snackbarHostState.showSnackbar("بدء سرد: $story")
                                        }
                                    }
                                )
                                4 -> DiagnosticsScreen(
                                    config = config,
                                    telemetry = telemetry,
                                    isSpeakerConnected = isConnected,
                                    connectionLabel = connectionLabel,
                                    onSaveWifi = { ssid, psk ->
                                        scope.launch {
                                            snackbarHostState.showSnackbar("جاري إرسال بيانات الواي فاي للسماعة...")
                                            val res = bridgeClient.setWifi(ssid, psk)
                                            repository.updateConfig { it.copy(wifiSsid = ssid, wifiPassword = psk) }
                                            repository.syncWithSpeaker()
                                            if (res.contains("WIFI_CONFIGURED_OK") || !res.contains("ERR")) {
                                                snackbarHostState.showSnackbar("تم ربط السماعة بالواي فاي بنجاح!")
                                            } else {
                                                snackbarHostState.showSnackbar("تم إرسال الإعدادات: $res")
                                            }
                                        }
                                    },
                                    onSaveApiKey = { key, model ->
                                        scope.launch {
                                            repository.updateConfig { it.copy(apiKey = key, liveModel = model) }
                                            repository.syncWithSpeaker()
                                            snackbarHostState.showSnackbar("تم حفظ مفتاح API ونموذج $model في السماعة!")
                                        }
                                    },
                                    onRefreshStatus = {
                                        scope.launch {
                                            val st = bridgeClient.getSpeakerStatus()
                                            if (st != "ERR-CONNECT") {
                                                isConnected = true
                                                connectionLabel = "متصل: $st"
                                                snackbarHostState.showSnackbar("استجابة السماعة: $st")
                                            } else {
                                                isConnected = false
                                                snackbarHostState.showSnackbar("تعذر الاتصال بالسماعة")
                                            }
                                        }
                                    },
                                    onOpenWifiSettings = {
                                        try {
                                            val intent = Intent(Settings.ACTION_WIFI_SETTINGS)
                                            context.startActivity(intent)
                                        } catch (_: Exception) {}
                                    },
                                    onConnectBluetooth = {
                                        scope.launch {
                                            val btOk = bridgeClient.connectBluetooth()
                                            if (btOk) {
                                                isConnected = true
                                                connectionLabel = "متصل عبر البلوتوث (Smaati_سماعتي)"
                                                snackbarHostState.showSnackbar("تم الاقتران بنجاح عبر البلوتوث!")
                                            } else {
                                                try {
                                                    val intent = Intent(Settings.ACTION_BLUETOOTH_SETTINGS)
                                                    context.startActivity(intent)
                                                } catch (_: Exception) {}
                                            }
                                        }
                                    }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
