package com.iraqi.smart.speaker.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.iraqi.smart.speaker.data.model.DeviceTelemetry
import com.iraqi.smart.speaker.data.model.SpeakerConfig
import com.iraqi.smart.speaker.ui.theme.AmberAccent
import com.iraqi.smart.speaker.ui.theme.CyanPrimary
import com.iraqi.smart.speaker.ui.theme.GreenAccent
import com.iraqi.smart.speaker.ui.theme.SurfaceDark

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiagnosticsScreen(
    config: SpeakerConfig,
    telemetry: DeviceTelemetry,
    isSpeakerConnected: Boolean = true,
    connectionLabel: String = "",
    onSaveWifi: (ssid: String, psk: String) -> Unit,
    onSaveApiKey: (apiKey: String, model: String) -> Unit,
    onRefreshStatus: () -> Unit,
    onOpenWifiSettings: () -> Unit = {},
    onConnectBluetooth: () -> Unit = {}
) {
    var wifiSsid by remember(config) { mutableStateOf(config.wifiSsid) }
    var wifiPsk by remember(config) { mutableStateOf(config.wifiPassword) }
    var pskVisible by remember { mutableStateOf(false) }

    var apiKey by remember(config) { mutableStateOf(config.apiKey) }
    var selectedModel by remember(config) { mutableStateOf(config.liveModel) }
    var apiKeyVisible by remember { mutableStateOf(false) }

    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp)
    ) {
        Text("الاتصال، الاقتران، وإعدادات Gemini", fontSize = 22.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Text("اقتران السماعة بالهاتف وربطها بالواي فاي المنزلي وحفظ إعدادات الذكاء الاصطناعي", fontSize = 13.sp, color = Color.Gray)

        Spacer(modifier = Modifier.height(14.dp))

        // Connection Status Banner
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = if (isSpeakerConnected) Color(0xFF0F382A) else Color(0xFF381515)
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                    Icon(
                        if (isSpeakerConnected) Icons.Default.CheckCircle else Icons.Default.Warning,
                        contentDescription = null,
                        tint = if (isSpeakerConnected) GreenAccent else AmberAccent,
                        modifier = Modifier.size(28.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            if (isSpeakerConnected) "السماعة متصلة ومقترنة" else "السماعة غير متصلة",
                            fontWeight = FontWeight.Bold,
                            color = Color.White,
                            fontSize = 15.sp
                        )
                        Text(
                            if (connectionLabel.isNotBlank()) connectionLabel else if (isSpeakerConnected) "IP: ${config.speakerIp}" else "اضغط على زر الاقتران أدناه",
                            color = if (isSpeakerConnected) GreenAccent else Color.LightGray,
                            fontSize = 12.sp
                        )
                    }
                }
                IconButton(onClick = onRefreshStatus) {
                    Icon(Icons.Default.Refresh, contentDescription = "تحديث", tint = CyanPrimary)
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Pairing Wizard Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.WifiTethering, contentDescription = null, tint = AmberAccent)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("خطوات الاقتران بالهاتف (لأول مرة أو تغيير الشبكة)", fontWeight = FontWeight.Bold, color = AmberAccent, fontSize = 15.sp)
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    "1. اضغط 3 مرات سريعة على زر رفع الصوت (+) بالسماعة لتفعيل وضع الاقتران.\n" +
                    "2. اتصل بشبكة الواي فاي 'Smaati_Setup' من هاتفك (بدون كلمة سر) أو اقترن بالبلوتوث 'Smaati_سماعتي'.\n" +
                    "3. بعد الاقتران، اكتب اسم وكلمة سر واي فاي المنزل أدناه واضغط حفظ.",
                    fontSize = 12.sp,
                    color = Color.LightGray,
                    lineHeight = 18.sp
                )

                Spacer(modifier = Modifier.height(14.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = onOpenWifiSettings,
                        modifier = Modifier.weight(1f).height(44.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = CyanPrimary)
                    ) {
                        Icon(Icons.Default.Wifi, contentDescription = null, tint = Color.Black, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("شبكة Smaati_Setup", fontWeight = FontWeight.Bold, color = Color.Black, fontSize = 12.sp)
                    }

                    OutlinedButton(
                        onClick = onConnectBluetooth,
                        modifier = Modifier.weight(1f).height(44.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = AmberAccent)
                    ) {
                        Icon(Icons.Default.Bluetooth, contentDescription = null, tint = AmberAccent, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("اقتران بلوتوث", fontWeight = FontWeight.Bold, color = AmberAccent, fontSize = 12.sp)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 1. Home Wi-Fi Setup Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Wifi, contentDescription = null, tint = GreenAccent)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("ربط السماعة بشبكة واي فاي المنزل", fontWeight = FontWeight.Bold, color = GreenAccent)
                }
                Text("تنقل السماعة إلى راوتر المنزل ليصبح المساعد الذكي متصلاً بالإنترنت دائماً", fontSize = 12.sp, color = Color.Gray)

                Spacer(modifier = Modifier.height(14.dp))

                OutlinedTextField(
                    value = wifiSsid,
                    onValueChange = { wifiSsid = it },
                    label = { Text("اسم شبكة واي فاي المنزل (SSID)") },
                    placeholder = { Text("مثال: CAPSULE أو Home_WiFi") },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                )

                Spacer(modifier = Modifier.height(10.dp))

                OutlinedTextField(
                    value = wifiPsk,
                    onValueChange = { wifiPsk = it },
                    label = { Text("كلمة مرور الواي فاي (Password)") },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    visualTransformation = if (pskVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    trailingIcon = {
                        IconButton(onClick = { pskVisible = !pskVisible }) {
                            Icon(if (pskVisible) Icons.Default.VisibilityOff else Icons.Default.Visibility, contentDescription = null)
                        }
                    }
                )

                Spacer(modifier = Modifier.height(14.dp))

                Button(
                    onClick = { onSaveWifi(wifiSsid, wifiPsk) },
                    modifier = Modifier.fillMaxWidth().height(48.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = GreenAccent)
                ) {
                    Icon(Icons.Default.WifiTethering, contentDescription = null, tint = Color.Black)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("حفظ وربط السماعة بالواي فاي", fontWeight = FontWeight.Bold, color = Color.Black)
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 2. Gemini Live API Key & Model Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.VpnKey, contentDescription = null, tint = AmberAccent)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("مفتاح Gemini API والنموذج الحي", fontWeight = FontWeight.Bold, color = AmberAccent)
                }
                Text("يتم حفظ المفتاح بصورة مشفرة في ذاكرة النظام الدائمة", fontSize = 12.sp, color = Color.Gray)

                Spacer(modifier = Modifier.height(14.dp))

                OutlinedTextField(
                    value = apiKey,
                    onValueChange = { apiKey = it },
                    label = { Text("Gemini API Key (AIzaSy...)") },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    visualTransformation = if (apiKeyVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    trailingIcon = {
                        IconButton(onClick = { apiKeyVisible = !apiKeyVisible }) {
                            Icon(if (apiKeyVisible) Icons.Default.VisibilityOff else Icons.Default.Visibility, contentDescription = null)
                        }
                    }
                )

                Spacer(modifier = Modifier.height(12.dp))

                Text("اختر نموذج المحادثة المباشرة:", fontSize = 13.sp, color = Color.LightGray)
                Spacer(modifier = Modifier.height(6.dp))

                val liveModels = listOf(
                    "gemini-2.0-flash-exp" to "Gemini 2.0 Flash Realtime (أسرع وأعلى جودة)",
                    "gemini-1.5-flash" to "Gemini 1.5 Flash (نموذج احتياطي خفيف)"
                )

                liveModels.forEach { (mKey, mLabel) ->
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = selectedModel == mKey,
                            onClick = { selectedModel = mKey }
                        )
                        Text(mLabel, fontSize = 13.sp, color = Color.White)
                    }
                }

                Spacer(modifier = Modifier.height(14.dp))

                Button(
                    onClick = { onSaveApiKey(apiKey, selectedModel) },
                    modifier = Modifier.fillMaxWidth().height(48.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = AmberAccent)
                ) {
                    Icon(Icons.Default.Save, contentDescription = null, tint = Color.Black)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("حفظ مفتاح API والنموذج في نظام السماعة", fontWeight = FontWeight.Bold, color = Color.Black)
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 3. Hardware Identity & Diagnostics Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("المعلومات العتادية للسماعة", fontWeight = FontWeight.Bold, color = GreenAccent)
                    IconButton(onClick = onRefreshStatus) {
                        Icon(Icons.Default.Refresh, contentDescription = "تحديث", tint = GreenAccent)
                    }
                }
                Spacer(modifier = Modifier.height(10.dp))
                DiagRow("طراز اللوحة (Board)", telemetry.boardModel)
                DiagRow("المعالج (Processor)", telemetry.soc)
                DiagRow("نظام التشغيل الداخلي", "Iraqi AI Speaker OS (Linux 3.10.14)")
                DiagRow("حالة منفذ التحكم الداخلي", "Port 8443 (Active Listen)", GreenAccent)
                DiagRow("متحكم الأزرار العتادي", "GPIO-Keys /dev/input/event0 (Active)", GreenAccent)
                DiagRow("التبديل للبلوتوث", "ضغطة مطولة 2 ثانية على زر المايك", AmberAccent)
                DiagRow("الذاكرة المتاحة للتخزين", telemetry.flashFree)
            }
        }
        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Composable
fun DiagRow(label: String, value: String, valueColor: Color = Color.White) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, fontSize = 13.sp, color = Color.Gray, modifier = Modifier.weight(0.45f))
        Text(value, fontSize = 13.sp, color = valueColor, fontWeight = FontWeight.Medium, modifier = Modifier.weight(0.55f))
    }
}
