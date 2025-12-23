package com.bassma.recipebuddy.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.spring
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.bassma.recipebuddy.data.model.DayPlanDto
import com.bassma.recipebuddy.data.model.MealPlanResponseDto
import com.bassma.recipebuddy.presentation.viewmodel.MealPlanPreset
import com.bassma.recipebuddy.presentation.viewmodel.MealPlanUiState
import com.bassma.recipebuddy.presentation.viewmodel.MealPlanViewModel
import com.bassma.recipebuddy.ui.components.common.PulsingDots

/**
 * Main screen for meal plan generation.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MealPlanScreen(
    viewModel: MealPlanViewModel,
    onRecipeClick: (String) -> Unit,
    onBackClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()
    val formState by viewModel.formState.collectAsState()
    
    var showCustomForm by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "Meal Plan Generator",
                        fontWeight = FontWeight.Bold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    ) { padding ->
        Box(
            modifier = modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when (val state = uiState) {
                is MealPlanUiState.Initial -> {
                    MealPlanInitialScreen(
                        onQuickPresetClick = { preset ->
                            viewModel.generateFromPreset(preset)
                        },
                        onCustomPlanClick = {
                            showCustomForm = true
                        }
                    )
                }
                
                is MealPlanUiState.Loading -> {
                    LoadingMealPlanScreen()
                }
                
                is MealPlanUiState.Success -> {
                    MealPlanResultScreen(
                        mealPlan = state.mealPlan,
                        onRecipeClick = onRecipeClick,
                        onGenerateNew = {
                            viewModel.resetForm()
                        }
                    )
                }
                
                is MealPlanUiState.Error -> {
                    ErrorMealPlanScreen(
                        message = state.message,
                        onRetry = {
                            viewModel.resetForm()
                        }
                    )
                }
            }

            // Custom form dialog
            if (showCustomForm) {
                CustomMealPlanDialog(
                    formState = formState,
                    viewModel = viewModel,
                    onDismiss = { showCustomForm = false },
                    onGenerate = {
                        viewModel.generateCustomMealPlan()
                        showCustomForm = false
                    }
                )
            }
        }
    }
}

/**
 * Initial screen with quick presets and custom option.
 */
@Composable
private fun MealPlanInitialScreen(
    onQuickPresetClick: (MealPlanPreset) -> Unit,
    onCustomPlanClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        item {
            // Header
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "🍽️",
                    style = MaterialTheme.typography.displayLarge
                )
                Text(
                    text = "Plan Your Meals",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center
                )
                Text(
                    text = "Choose a quick preset or create a custom plan",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center
                )
            }
        }

        item {
            Divider(modifier = Modifier.padding(vertical = 8.dp))
        }

        item {
            Text(
                text = "Quick Presets",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 8.dp)
            )
        }

        items(MealPlanPreset.values().toList()) { preset ->
            PresetCard(
                preset = preset,
                onClick = { onQuickPresetClick(preset) }
            )
        }

        item {
            Divider(modifier = Modifier.padding(vertical = 16.dp))
        }

        item {
            // Custom plan button
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(onClick = onCustomPlanClick),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.tertiaryContainer
                ),
                shape = RoundedCornerShape(16.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "⚙️",
                                style = MaterialTheme.typography.headlineSmall
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Text(
                                text = "Custom Meal Plan",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Fine-tune every detail: nutrition goals, dietary preferences, excluded ingredients, and more",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onTertiaryContainer.copy(alpha = 0.8f)
                        )
                    }
                    Icon(
                        imageVector = Icons.Default.ArrowForward,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onTertiaryContainer,
                        modifier = Modifier.size(32.dp)
                    )
                }
            }
        }

        item {
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

/**
 * Card for displaying a preset option.
 */
@Composable
private fun PresetCard(
    preset: MealPlanPreset,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Emoji icon
            Box(
                modifier = Modifier
                    .size(60.dp)
                    .background(
                        color = MaterialTheme.colorScheme.primaryContainer,
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = preset.emoji,
                    style = MaterialTheme.typography.headlineMedium
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = preset.displayName,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = preset.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    InfoChip(text = "${preset.calories} cal/day")
                    InfoChip(text = "${preset.days} days")
                }
            }

            Icon(
                imageVector = Icons.Default.KeyboardArrowRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun InfoChip(text: String) {
    Surface(
        color = MaterialTheme.colorScheme.secondaryContainer,
        shape = RoundedCornerShape(8.dp)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSecondaryContainer,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

/**
 * Loading screen while generating meal plan.
 */
@Composable
private fun LoadingMealPlanScreen() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = "👨‍🍳",
                style = MaterialTheme.typography.displayLarge
            )
            Spacer(modifier = Modifier.height(24.dp))
            PulsingDots()
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Crafting your perfect meal plan...",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Analyzing nutrition, balancing flavors",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Error screen with retry option.
 */
@Composable
private fun ErrorMealPlanScreen(
    message: String,
    onRetry: () -> Unit
) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(32.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.error,
                modifier = Modifier.size(64.dp)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Oops! Something went wrong",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = onRetry) {
                Icon(Icons.Default.Refresh, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Try Again")
            }
        }
    }
}

/**
 * Result screen showing the generated meal plan.
 */
@Composable
private fun MealPlanResultScreen(
    mealPlan: MealPlanResponseDto,
    onRecipeClick: (String) -> Unit,
    onGenerateNew: () -> Unit
) {
    val days = mealPlan.getDays()
    val summary = mealPlan.summary
    
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Header with total nutrition
        item {
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                ),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "Your Meal Plan",
                                style = MaterialTheme.typography.headlineSmall,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "${days.size} days • ${summary?.totalMeals ?: 0} meals",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                            )
                        }
                        Text(text = "✨", style = MaterialTheme.typography.displaySmall)
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Summary nutrition
                    if (summary != null) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            NutritionBadge(
                                label = "Avg Cal/Day",
                                value = "${summary.avgCaloriesPerDay?.toInt() ?: 0}",
                                emoji = "🔥"
                            )
                            NutritionBadge(
                                label = "Avg Protein",
                                value = "${summary.avgProteinPerDay?.toInt() ?: 0}g",
                                emoji = "💪"
                            )
                            NutritionBadge(
                                label = "Total Meals",
                                value = "${summary.totalMeals ?: 0}",
                                emoji = "🍽️"
                            )
                            NutritionBadge(
                                label = "Days",
                                value = "${summary.totalDays ?: days.size}",
                                emoji = "📅"
                            )
                        }
                    }
                }
            }
        }

        // Day by day meal plans
        items(days) { day ->
            DayPlanCard(
                day = day,
                onRecipeClick = onRecipeClick
            )
        }

        // Generate new button
        item {
            OutlinedButton(
                onClick = onGenerateNew,
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Default.Refresh, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Generate New Plan")
            }
        }

        item {
            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
private fun NutritionBadge(
    label: String,
    value: String,
    emoji: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = emoji, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
        )
    }
}

@Composable
private fun DayPlanCard(
    day: DayPlanDto,
    onRecipeClick: (String) -> Unit
) {
    val dailyTotals = day.dailyTotals
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Day header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Day ${day.day ?: 0}",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    day.date?.let { date ->
                        Text(
                            text = date,
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                if (dailyTotals != null) {
                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = "${dailyTotals.calories?.toInt() ?: 0} cal",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = "P:${dailyTotals.protein?.toInt() ?: 0}g • F:${dailyTotals.fat?.toInt() ?: 0}g",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Meals
            val meals = day.meals ?: emptyList()
            meals.forEach { meal ->
                MealItem(
                    meal = meal,
                    onClick = { 
                        meal.id?.let { id -> onRecipeClick(id.toString()) }
                    }
                )
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
private fun MealItem(
    meal: com.bassma.recipebuddy.data.model.MealDto,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        color = MaterialTheme.colorScheme.surfaceVariant,
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Meal type emoji
            val mealTypeStr = meal.mealType ?: "meal"
            val emoji = when (mealTypeStr.lowercase()) {
                "breakfast" -> "🍳"
                "lunch" -> "🍱"
                "dinner" -> "🍽️"
                "snack" -> "🍪"
                else -> "🍴"
            }
            
            Text(
                text = emoji,
                style = MaterialTheme.typography.headlineSmall,
                modifier = Modifier.size(40.dp)
            )

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = mealTypeStr.replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = meal.title ?: "Recipe",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium
                )
                // Show calories from the meal directly
                val calories = meal.calories ?: meal.nutrition?.calories
                if (calories != null) {
                    Text(
                        text = "${calories.toInt()} cal",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Icon(
                imageVector = Icons.Default.KeyboardArrowRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

// Custom dialog will be in next part due to length...
@Composable
private fun CustomMealPlanDialog(
    formState: com.bassma.recipebuddy.presentation.viewmodel.MealPlanFormState,
    viewModel: MealPlanViewModel,
    onDismiss: () -> Unit,
    onGenerate: () -> Unit
) {
    // Placeholder - Full implementation would go here
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Custom Meal Plan") },
        text = { Text("Custom form coming soon...") },
        confirmButton = {
            TextButton(onClick = onGenerate) {
                Text("Generate")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}
