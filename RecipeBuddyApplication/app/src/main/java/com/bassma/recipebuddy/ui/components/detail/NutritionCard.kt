package com.bassma.recipebuddy.ui.components.detail

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.bassma.recipebuddy.domain.model.Nutrition

/**
 * Card displaying nutritional information for a recipe.
 */
@Composable
fun NutritionCard(
    nutrition: Nutrition,
    modifier: Modifier = Modifier
) {
    // Check if all values are essentially 0
    val hasNutritionData = nutrition.calories > 0 || nutrition.protein > 0 || 
                           nutrition.fat > 0 || nutrition.carbs > 0
    
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "📊 Nutrition Info",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            if (!hasNutritionData) {
                Text(
                    text = "Nutrition information not available for this recipe.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            } else {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    NutritionItem(
                        emoji = "🔥",
                        label = "Calories",
                        value = if (nutrition.calories > 0) "${nutrition.calories.toInt()}" else "N/A"
                    )
                    NutritionItem(
                        emoji = "💪",
                        label = "Protein",
                        value = if (nutrition.protein > 0) "${String.format("%.1f", nutrition.protein)}g" else "N/A"
                    )
                    NutritionItem(
                        emoji = "🧈",
                        label = "Fat",
                        value = if (nutrition.fat > 0) "${String.format("%.1f", nutrition.fat)}g" else "N/A"
                    )
                    NutritionItem(
                        emoji = "🍬",
                        label = "Carbs",
                        value = if (nutrition.carbs > 0) "${String.format("%.1f", nutrition.carbs)}g" else "N/A"
                    )
                }
            }
        }
    }
}

@Composable
private fun NutritionItem(
    emoji: String,
    label: String,
    value: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = emoji,
            style = MaterialTheme.typography.headlineSmall
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )
    }
}
