package com.bassma.recipebuddy.ui.components.home

import androidx.compose.animation.core.*
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlin.random.Random

/**
 * Data class for floating emoji animation
 */
data class FloatingEmoji(
    val emoji: String,
    val startX: Float,
    val endX: Float,
    val delay: Long,
    val duration: Int
)

/**
 * Background floating food emojis for visual appeal.
 */
@Composable
fun FloatingFoodEmojis() {
    val emojis = listOf("🍕", "🍔", "🌮", "🍜", "🍣", "🥗", "🍝", "🥘", "🍲", "🥙", "🍛", "🥪")
    val screenWidth = LocalConfiguration.current.screenWidthDp
    
    val floatingEmojis = remember {
        (1..8).map {
            FloatingEmoji(
                emoji = emojis.random(),
                startX = Random.nextFloat() * screenWidth,
                endX = Random.nextFloat() * screenWidth,
                delay = Random.nextLong(0, 3000),
                duration = Random.nextInt(4000, 8000)
            )
        }
    }
    
    Box(modifier = Modifier.fillMaxSize()) {
        floatingEmojis.forEach { emoji ->
            FloatingEmojiItem(emoji)
        }
    }
}

@Composable
private fun FloatingEmojiItem(emoji: FloatingEmoji) {
    var startAnimation by remember { mutableStateOf(false) }
    
    LaunchedEffect(Unit) {
        delay(emoji.delay)
        startAnimation = true
    }
    
    val infiniteTransition = rememberInfiniteTransition(label = "emoji_transition")
    
    val yOffset by infiniteTransition.animateFloat(
        initialValue = 800f,
        targetValue = -100f,
        animationSpec = infiniteRepeatable(
            animation = tween(emoji.duration, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "y_offset"
    )
    
    val xOffset by infiniteTransition.animateFloat(
        initialValue = emoji.startX,
        targetValue = emoji.endX,
        animationSpec = infiniteRepeatable(
            animation = tween(emoji.duration, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "x_offset"
    )
    
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.1f,
        targetValue = 0.3f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )
    
    if (startAnimation) {
        Text(
            text = emoji.emoji,
            modifier = Modifier
                .offset(x = xOffset.dp, y = yOffset.dp)
                .alpha(alpha),
            fontSize = 28.sp
        )
    }
}
