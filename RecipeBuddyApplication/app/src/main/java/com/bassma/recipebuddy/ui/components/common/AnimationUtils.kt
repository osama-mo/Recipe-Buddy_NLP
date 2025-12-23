package com.bassma.recipebuddy.ui.components.common

import androidx.compose.animation.core.*
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput

/**
 * Common animation utilities and modifiers.
 */

/**
 * Common easing function for smooth animations.
 */
val EaseInOutQuad: Easing = Easing { fraction ->
    if (fraction < 0.5f) {
        2 * fraction * fraction
    } else {
        1 - (-2 * fraction + 2).let { it * it } / 2
    }
}

/**
 * Applies a bouncy press animation to any composable.
 */
@Composable
fun Modifier.bounceClick(
    scaleDown: Float = 0.95f,
    onClick: () -> Unit
): Modifier {
    var isPressed by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (isPressed) scaleDown else 1f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "bounce_scale"
    )
    
    return this
        .scale(scale)
        .pointerInput(Unit) {
            detectTapGestures(
                onPress = {
                    isPressed = true
                    tryAwaitRelease()
                    isPressed = false
                    onClick()
                }
            )
        }
}

/**
 * Staggered animation for list items.
 */
@Composable
fun StaggeredAnimatedItem(
    index: Int,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    var visible by remember { mutableStateOf(false) }
    
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(index * 50L)
        visible = true
    }
    
    val animatedAlpha by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = tween(
            durationMillis = 400,
            easing = FastOutSlowInEasing
        ),
        label = "item_alpha"
    )
    
    val animatedOffset by animateFloatAsState(
        targetValue = if (visible) 0f else 50f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "item_offset"
    )
    
    Box(
        modifier = modifier.graphicsLayer {
            alpha = animatedAlpha
            translationY = animatedOffset
        }
    ) {
        content()
    }
}

/**
 * Pulsating animation for loading or attention-grabbing elements.
 */
@Composable
fun Modifier.pulsate(): Modifier {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_scale"
    )
    
    return this.scale(scale)
}

/**
 * Floating animation for decorative elements.
 */
@Composable
fun Modifier.floatingAnimation(): Modifier {
    val infiniteTransition = rememberInfiniteTransition(label = "float")
    val offsetY by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 15f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = EaseInOutQuad),
            repeatMode = RepeatMode.Reverse
        ),
        label = "float_offset"
    )
    
    return this.graphicsLayer {
        translationY = offsetY
    }
}

/**
 * Animated section that fades and slides in.
 */
@Composable
fun AnimatedSection(
    visible: Boolean,
    delay: Int,
    content: @Composable () -> Unit
) {
    var show by remember { mutableStateOf(false) }
    
    LaunchedEffect(visible) {
        if (visible) {
            kotlinx.coroutines.delay(delay.toLong())
            show = true
        }
    }
    
    val alpha by animateFloatAsState(
        targetValue = if (show) 1f else 0f,
        animationSpec = tween(400),
        label = "section_alpha"
    )
    
    val offset by animateFloatAsState(
        targetValue = if (show) 0f else 40f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "section_offset"
    )
    
    Box(
        modifier = Modifier.graphicsLayer {
            this.alpha = alpha
            translationY = offset
        }
    ) {
        content()
    }
}
