package com.bassma.recipebuddy.ui.components.detail

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay

/**
 * Animated category chip for recipe detail screen.
 */
@Composable
fun AnimatedCategoryChip(
    category: String,
    delay: Int
) {
    var visible by remember { mutableStateOf(false) }
    
    LaunchedEffect(Unit) {
        delay(delay.toLong())
        visible = true
    }
    
    val scale by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "chip_scale"
    )
    
    Surface(
        modifier = Modifier.scale(scale),
        shape = RoundedCornerShape(20.dp),
        color = MaterialTheme.colorScheme.secondaryContainer
    ) {
        Text(
            text = category.replaceFirstChar { it.uppercase() },
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSecondaryContainer
        )
    }
}

/**
 * Animated ingredient item with staggered entrance.
 */
@Composable
fun AnimatedIngredientItem(
    ingredient: String,
    index: Int,
    visible: Boolean
) {
    var show by remember { mutableStateOf(false) }
    
    LaunchedEffect(visible) {
        if (visible) {
            delay((300 + index * 50).toLong())
            show = true
        }
    }
    
    val alpha by animateFloatAsState(
        targetValue = if (show) 1f else 0f,
        animationSpec = tween(300),
        label = "ingredient_alpha"
    )
    
    val offsetX by animateFloatAsState(
        targetValue = if (show) 0f else -20f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy),
        label = "ingredient_offset"
    )
    
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .graphicsLayer {
                this.alpha = alpha
                translationX = offsetX
            },
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.primary)
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = ingredient,
            style = MaterialTheme.typography.bodyLarge
        )
    }
}

/**
 * Animated direction step with number badge.
 */
@Composable
fun AnimatedDirectionStep(
    step: Int,
    instruction: String,
    visible: Boolean,
    delay: Int
) {
    var show by remember { mutableStateOf(false) }
    
    LaunchedEffect(visible) {
        if (visible) {
            delay((400 + delay).toLong())
            show = true
        }
    }
    
    val alpha by animateFloatAsState(
        targetValue = if (show) 1f else 0f,
        animationSpec = tween(400),
        label = "step_alpha"
    )
    
    val scale by animateFloatAsState(
        targetValue = if (show) 1f else 0.8f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy),
        label = "step_scale"
    )
    
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 10.dp)
            .graphicsLayer {
                this.alpha = alpha
                scaleX = scale
                scaleY = scale
            },
        verticalAlignment = Alignment.Top
    ) {
        Surface(
            shape = CircleShape,
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(32.dp)
        ) {
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier.fillMaxSize()
            ) {
                Text(
                    text = "$step",
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimary
                )
            }
        }
        Spacer(modifier = Modifier.width(14.dp))
        Text(
            text = instruction,
            style = MaterialTheme.typography.bodyLarge,
            modifier = Modifier.weight(1f),
            lineHeight = 24.sp
        )
    }
}

/**
 * Generic animated section wrapper for detail content.
 */
@Composable
fun AnimatedDetailSection(
    visible: Boolean,
    delay: Int,
    content: @Composable () -> Unit
) {
    var show by remember { mutableStateOf(false) }
    
    LaunchedEffect(visible) {
        if (visible) {
            delay(delay.toLong())
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
