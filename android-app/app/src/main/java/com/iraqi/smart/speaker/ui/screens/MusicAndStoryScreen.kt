package com.iraqi.smart.speaker.ui.screens

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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.iraqi.smart.speaker.ui.theme.AmberAccent
import com.iraqi.smart.speaker.ui.theme.CyanPrimary
import com.iraqi.smart.speaker.ui.theme.GreenAccent
import com.iraqi.smart.speaker.ui.theme.SurfaceDark

@Composable
fun MusicAndStoryScreen(
    onPlayTrack: (String) -> Unit,
    onStopTrack: () -> Unit,
    onStartStory: (String) -> Unit
) {
    var isPlaying by remember { mutableStateOf(false) }
    var selectedSleepTimer by remember { mutableStateOf("30 دقيقة") }
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp)
    ) {
        // Section: Music Center
        Text("مركز الموسيقى والصوتيات العراقية", fontSize = 22.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Text("تشغيل الأغاني العراقية المحفوظة مع مؤقت النوم", fontSize = 13.sp, color = Color.Gray)

        Spacer(modifier = Modifier.height(16.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.MusicNote, contentDescription = null, tint = CyanPrimary, modifier = Modifier.size(32.dp))
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text("حلو حبك", fontWeight = FontWeight.Bold, color = Color.White, fontSize = 16.sp)
                        Text("هيثم يوسف • صوت عالي الجودة", fontSize = 13.sp, color = Color.Gray)
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(onClick = { /* Previous */ }) {
                        Icon(Icons.Default.SkipPrevious, contentDescription = null, tint = Color.White)
                    }
                    Spacer(modifier = Modifier.width(16.dp))
                    FloatingActionButton(
                        onClick = {
                            isPlaying = !isPlaying
                            if (isPlaying) onPlayTrack("helo_hobak.m4a") else onStopTrack()
                        },
                        containerColor = CyanPrimary,
                        contentColor = Color.Black
                    ) {
                        Icon(if (isPlaying) Icons.Default.Pause else Icons.Default.PlayArrow, contentDescription = null)
                    }
                    Spacer(modifier = Modifier.width(16.dp))
                    IconButton(onClick = { /* Next */ }) {
                        Icon(Icons.Default.SkipNext, contentDescription = null, tint = Color.White)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Section: Story Mode
        Text("حكايات وقصص عراقية وتراثية", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Text("قصص قبل النوم للأطفال، قصص بغدادية، وحكايات شعبية مقسمة إلى فصول", fontSize = 13.sp, color = Color.Gray)

        Spacer(modifier = Modifier.height(12.dp))

        val stories = listOf(
            "حكاية ألف ليلة وليلة في بغداد" to "تراث بغدادي عريق",
            "قصة السمكة الذهبية وشط العرب" to "قصة أطفال هادئة",
            "سالفة ابن دلة والفانوس العجيب" to "قصة شعبية فكاهية"
        )

        stories.forEach { (title, subtitle) ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 6.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                shape = RoundedCornerShape(14.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(title, fontWeight = FontWeight.SemiBold, color = Color.White)
                        Text(subtitle, fontSize = 12.sp, color = Color.Gray)
                    }
                    Button(
                        onClick = { onStartStory(title) },
                        colors = ButtonDefaults.buttonColors(containerColor = AmberAccent),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Text("اسمع القصة", color = Color.Black, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(24.dp))
    }
}
