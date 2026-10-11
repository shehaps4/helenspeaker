package com.iraqi.smart.speaker.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.iraqi.smart.speaker.data.model.DeviceTelemetry
import com.iraqi.smart.speaker.data.model.SpeakerConfig
import com.iraqi.smart.speaker.ui.theme.AmberAccent
import com.iraqi.smart.speaker.ui.theme.CyanPrimary
import com.iraqi.smart.speaker.ui.theme.GreenAccent
import com.iraqi.smart.speaker.ui.theme.SurfaceDark

@Composable
fun DashboardScreen(
    config: SpeakerConfig,
    telemetry: DeviceTelemetry,
    onStartTalk: () -> Unit,
    onToggleBluetoothMode: (Boolean) -> Unit,
    onVolumeChange: (Int) -> Unit
) {
    var volume by remember { mutableStateOf(telemetry.currentVolume.toFloat()) }
    var isBtMode by remember { mutableStateOf(config.bluetoothMode == "A2DP_SPEAKER") }

    // Pulsing aura animation for RGB
    val infiniteTransition = rememberInfiniteTransition(label = "rgb_pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Speaker Card & Visual Glow
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(24.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Speaker circular icon with RGB aura
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(140.dp)
                        .scale(pulseScale)
                        .background(
                            Brush.radialGradient(
                                colors = listOf(CyanPrimary.copy(alpha = 0.4f), Color.Transparent)
                            ),
                            shape = CircleShape
                        )
                ) {
                    Box(
                        modifier = Modifier
                            .size(100.dp)
                            .clip(CircleShape)
                            .background(Color(0xFF111827))
                            .border(3.dp, CyanPrimary, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Speaker,
                            contentDescription = "Speaker",
                            tint = CyanPrimary,
                            modifier = Modifier.size(54.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = "${config.characterName} (${config.speakerId})",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    text = "متصل بنجاح • Ingenic X1800 MIPS Linux",
                    fontSize = 13.sp,
                    color = GreenAccent
                )
                Text(
                    text = "النموذج: ${config.liveModel}",
                    fontSize = 12.sp,
                    color = AmberAccent
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Big Iraqi Live Talk Button
        Button(
            onClick = onStartTalk,
            modifier = Modifier
                .fillMaxWidth()
                .height(64.dp),
            colors = ButtonDefaults.buttonColors(containerColor = CyanPrimary),
            shape = RoundedCornerShape(18.dp)
        ) {
            Icon(Icons.Default.Mic, contentDescription = null, tint = Color.Black)
            Spacer(modifier = Modifier.width(10.dp))
            Text(
                text = "تحدث مع ${config.characterName} بالعراقي (مباشر)",
                fontSize = 17.sp,
                fontWeight = FontWeight.Bold,
                color = Color.Black
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Bluetooth Speaker Mode Toggle
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(18.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = "وضع سماعة بلوتوث (A2DP)",
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Text(
                        text = if (isBtMode) "مفعل: تشغيل الصوت من الهاتف عبر البلوتوث" else "وضع المساعد الذكي نشط",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }
                Switch(
                    checked = isBtMode,
                    onCheckedChange = {
                        isBtMode = it
                        onToggleBluetoothMode(it)
                    }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Volume Slider Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("مستوى الصوت العتادي", color = Color.White, fontWeight = FontWeight.Medium)
                    Text("${volume.toInt()}%", color = CyanPrimary, fontWeight = FontWeight.Bold)
                }
                Slider(
                    value = volume,
                    onValueChange = {
                        volume = it
                        onVolumeChange(it.toInt())
                    },
                    valueRange = 0f..100f
                )
            }
        }
    }
}
