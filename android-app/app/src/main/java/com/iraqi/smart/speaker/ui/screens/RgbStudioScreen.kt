package com.iraqi.smart.speaker.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.iraqi.smart.speaker.data.model.SpeakerConfig
import com.iraqi.smart.speaker.ui.theme.CyanPrimary
import com.iraqi.smart.speaker.ui.theme.SurfaceDark

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RgbStudioScreen(
    config: SpeakerConfig,
    onApplyRgb: (colorHex: String, mode: String, brightness: Int) -> Unit
) {
    var selectedColor by remember { mutableStateOf(config.rgbColor) }
    var selectedMode by remember { mutableStateOf(config.rgbMode) }
    var brightness by remember { mutableStateOf(config.rgbBrightness.toFloat()) }
    var isRgbEnabled by remember { mutableStateOf(config.rgbEnabled) }

    val presetColors = listOf(
        "#00DCFF" to Color(0xFF00DCFF),
        "#00FF64" to Color(0xFF00FF64),
        "#FFA000" to Color(0xFFFFA000),
        "#A855F7" to Color(0xFFA855F7),
        "#FF0033" to Color(0xFFFF0033),
        "#0055FF" to Color(0xFF0055FF),
        "#FFFFFF" to Color(0xFFFFFFFF)
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text("استوديو الإضاءة التفاعلية AW2015", fontSize = 22.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Text("تحكم بإضاءة الـ RGB المدمجة بالسماعة والتأثيرات الصوتية", fontSize = 13.sp, color = Color.Gray)

        Spacer(modifier = Modifier.height(16.dp))

        // Enable Switch Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("تشغيل إضاءة الـ RGB", color = Color.White, fontWeight = FontWeight.Medium)
                Switch(checked = isRgbEnabled, onCheckedChange = {
                    isRgbEnabled = it
                    if (!it) onApplyRgb("#000000", "off", 0)
                })
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Color Palette Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("اختيار اللون:", color = Color.White, fontWeight = FontWeight.SemiBold)
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    presetColors.forEach { (hex, color) ->
                        Box(
                            modifier = Modifier
                                .size(42.dp)
                                .clip(CircleShape)
                                .background(color)
                                .border(
                                    width = if (selectedColor == hex) 3.dp else 0.dp,
                                    color = if (selectedColor == hex) Color.White else Color.Transparent,
                                    shape = CircleShape
                                )
                                .clickable {
                                    selectedColor = hex
                                    onApplyRgb(hex, selectedMode, brightness.toInt())
                                }
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Modes Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("أنماط الحركة والتأثيرات:", color = Color.White, fontWeight = FontWeight.SemiBold)
                Spacer(modifier = Modifier.height(8.dp))
                val modes = listOf(
                    "solid" to "لون ثابت",
                    "pulse" to "نبض تنفسي (Breathing)",
                    "listening" to "نمط الاستماع (سماوي نابض)",
                    "thinking" to "نمط التفكير (عنبري ثابت)",
                    "speaking" to "نمط التحدث (أخضر تفاعلي)"
                )
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    modes.forEach { (key, label) ->
                        FilterChip(
                            selected = selectedMode == key,
                            onClick = {
                                selectedMode = key
                                onApplyRgb(selectedColor, key, brightness.toInt())
                            },
                            label = { Text(label) },
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Brightness Slider Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("شدة السطوع", color = Color.White)
                    Text("${(brightness * 100 / 255).toInt()}%", color = CyanPrimary, fontWeight = FontWeight.Bold)
                }
                Slider(
                    value = brightness,
                    onValueChange = {
                        brightness = it
                        onApplyRgb(selectedColor, selectedMode, it.toInt())
                    },
                    valueRange = 0f..255f
                )
            }
        }
    }
}
