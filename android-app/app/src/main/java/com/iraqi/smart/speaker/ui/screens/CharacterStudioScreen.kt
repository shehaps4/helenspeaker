package com.iraqi.smart.speaker.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.iraqi.smart.speaker.data.model.SpeakerConfig
import com.iraqi.smart.speaker.data.model.SyncStatus
import com.iraqi.smart.speaker.ui.theme.AmberAccent
import com.iraqi.smart.speaker.ui.theme.CyanPrimary
import com.iraqi.smart.speaker.ui.theme.GreenAccent
import com.iraqi.smart.speaker.ui.theme.SurfaceDark

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CharacterStudioScreen(
    config: SpeakerConfig,
    onSaveConfig: (SpeakerConfig) -> Unit,
    onPreviewVoice: (String) -> Unit
) {
    var charName by remember(config) { mutableStateOf(config.characterName) }
    var dialect by remember(config) { mutableStateOf(config.dialect) }
    var voiceGender by remember(config) { mutableStateOf(config.voiceGender) }
    var voiceName by remember(config) { mutableStateOf(config.voiceName) }
    var relStyle by remember(config) { mutableStateOf(config.relationshipStyle) }

    var romance by remember(config) { mutableStateOf(config.romanceLevel.toFloat()) }
    var boldness by remember(config) { mutableStateOf(config.boldnessLevel.toFloat()) }
    var humor by remember(config) { mutableStateOf(config.humorLevel.toFloat()) }

    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp)
    ) {
        Text("استوديو الشخصية والمشاعر العراقية", fontSize = 22.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Text("تحكم كامل بالاسم، نبرة الصوت، المشاعر، ومستوى الجراءة والعلاقة", fontSize = 13.sp, color = Color.Gray)

        Spacer(modifier = Modifier.height(16.dp))

        // 1. Character Name
        OutlinedTextField(
            value = charName,
            onValueChange = { charName = it },
            label = { Text("اسم الشخصية (مثال: ريام، سارة، حيدر، شمس)") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(14.dp)
        )

        Spacer(modifier = Modifier.height(18.dp))

        // 2. Voice Gender & Preset Voices
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("نبرة الصوت والصوت المعتمد (Live Voice Model)", fontWeight = FontWeight.Bold, color = CyanPrimary)
                Spacer(modifier = Modifier.height(8.dp))

                // Gender Toggle
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    FilterChip(
                        selected = voiceGender == "female",
                        onClick = {
                            voiceGender = "female"
                            voiceName = "Kore"
                        },
                        label = { Text("أنثوي (Feminine)") },
                        modifier = Modifier.weight(1f)
                    )
                    FilterChip(
                        selected = voiceGender == "male",
                        onClick = {
                            voiceGender = "male"
                            voiceName = "Puck"
                        },
                        label = { Text("ذكري (Masculine)") },
                        modifier = Modifier.weight(1f)
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))
                Text("اختر الصوت المحدد:", fontSize = 13.sp, color = Color.LightGray)
                Spacer(modifier = Modifier.height(6.dp))

                val availableVoices = if (voiceGender == "female") {
                    listOf(
                        "Kore" to "Kore (ناعم، دافئ، جذاب)",
                        "Aoede" to "Aoede (عاطفي، شجي، عميق)",
                        "Leda" to "Leda (هادئ، واثق، ساحر)"
                    )
                } else {
                    listOf(
                        "Puck" to "Puck (مرح، سريع البديهة، مشاكس)",
                        "Fenrir" to "Fenrir (رجولي، فخم، قوي)",
                        "Charon" to "Charon (وقور، حنون، هادئ)"
                    )
                }

                availableVoices.forEach { (vKey, vDesc) ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = voiceName == vKey,
                            onClick = { voiceName = vKey }
                        )
                        Text(vDesc, modifier = Modifier.weight(1f), fontSize = 13.sp, color = Color.White)
                        IconButton(onClick = { onPreviewVoice(vKey) }) {
                            Icon(Icons.Default.VolumeUp, contentDescription = "اختبار الصوت", tint = AmberAccent)
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(18.dp))

        // 3. Dialect Selector
        Text("نمط اللهجة العراقية:", fontWeight = FontWeight.SemiBold, color = Color.White)
        Spacer(modifier = Modifier.height(6.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            val dialects = listOf(
                "baghdadi" to "بغدادي",
                "general_iq" to "عام",
                "southern_iq" to "جنوبي",
                "simplified_ar" to "مبسط"
            )
            dialects.forEach { (key, label) ->
                FilterChip(
                    selected = dialect == key,
                    onClick = { dialect = key },
                    label = { Text(label) }
                )
            }
        }

        Spacer(modifier = Modifier.height(18.dp))

        // 4. Relationship Style (8 options as requested)
        Text("مستوى العلاقة والأسلوب:", fontWeight = FontWeight.SemiBold, color = Color.White)
        Spacer(modifier = Modifier.height(6.dp))

        val relationshipStyles = listOf(
            "Romantic" to "Romantic - رومانسي وعاطفي دافئ جداً",
            "HornyLover" to "HornyLover - عاشق شغوف وجريء جداً",
            "SexyLover" to "SexyLover - حبيب مشاكس مغري وجريء",
            "PornLover" to "PornLover - أقصى درجات التحرر والجراءة",
            "CloseFriend" to "CloseFriend - صديق مقرّب وبير أسرار",
            "Friend" to "Friend - صديق وفيّ ولطيف",
            "Familiar" to "Familiar - معرفة مألوفة وعفوية",
            "New" to "New - بداية تعارف راقية"
        )

        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            relationshipStyles.forEach { (key, label) ->
                FilterChip(
                    selected = relStyle == key,
                    onClick = { relStyle = key },
                    label = { Text(label) },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // 5. Emotion Sliders (3 sliders as explicitly requested)
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("تحديد مستويات المشاعر والتفاعل", fontWeight = FontWeight.Bold, color = AmberAccent)
                Spacer(modifier = Modifier.height(8.dp))

                EmotionSliderItem("الرومانسية والغزل", romance, "%") { romance = it }
                EmotionSliderItem("الشهوة والجراءة في التعبير", boldness, "%") { boldness = it }
                EmotionSliderItem("المزاح والمشاكسة العراقية", humor, "%") { humor = it }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // 6. Sync Status & Save to Speaker
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            val (statusText, statusColor) = when (config.syncStatus) {
                SyncStatus.SAVED_ON_SPEAKER -> "تم الحفظ والتطبيق داخل نظام السماعة الذكية بنجاح" to GreenAccent
                SyncStatus.PENDING_SYNC -> "تغييرات بانتظار الإرسال إلى السماعة" to AmberAccent
                SyncStatus.SAVED_LOCAL_PHONE -> "محفوظ في الهاتف (جاهز للإرسال للسماعة)" to CyanPrimary
                SyncStatus.SYNC_FAILED -> "فشل إرسال الإعدادات للسماعة" to Color.Red
                SyncStatus.NOT_SUPPORTED -> "غير مدعوم" to Color.Gray
            }
            Text("حالة النظام: ", fontSize = 13.sp, color = Color.Gray)
            Text(statusText, fontSize = 13.sp, color = statusColor, fontWeight = FontWeight.Bold)
        }

        Spacer(modifier = Modifier.height(14.dp))

        Button(
            onClick = {
                val updated = config.copy(
                    characterName = charName.ifBlank { "ريام" },
                    dialect = dialect,
                    voiceGender = voiceGender,
                    voiceName = voiceName,
                    relationshipStyle = relStyle,
                    romanceLevel = romance.toInt(),
                    boldnessLevel = boldness.toInt(),
                    humorLevel = humor.toInt()
                )
                onSaveConfig(updated)
            },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(containerColor = CyanPrimary)
        ) {
            Icon(Icons.Default.Save, contentDescription = null, tint = Color.Black)
            Spacer(modifier = Modifier.width(8.dp))
            Text("حفظ التغييرات داخل نظام السماعة الذكية", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.Black)
        }
    }
}

@Composable
fun EmotionSliderItem(title: String, value: Float, unit: String, onValueChange: (Float) -> Unit) {
    Column(modifier = Modifier.padding(vertical = 8.dp)) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(title, fontSize = 14.sp, color = Color.White)
            Text("${value.toInt()}$unit", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = CyanPrimary)
        }
        Slider(
            value = value,
            onValueChange = onValueChange,
            valueRange = 0f..100f,
            colors = SliderDefaults.colors(
                thumbColor = CyanPrimary,
                activeTrackColor = CyanPrimary,
                inactiveTrackColor = Color.DarkGray
            )
        )
    }
}
