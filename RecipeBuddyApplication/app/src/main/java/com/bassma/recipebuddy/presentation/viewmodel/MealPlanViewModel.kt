package com.bassma.recipebuddy.presentation.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.bassma.recipebuddy.data.model.MealPlanPreferencesDto
import com.bassma.recipebuddy.data.model.MealPlanRequestDto
import com.bassma.recipebuddy.data.model.MealPlanResponseDto
import com.bassma.recipebuddy.data.model.MealPlanNutritionGoalsDto
import com.bassma.recipebuddy.di.AppModule
import com.bassma.recipebuddy.domain.repository.RecipeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for managing meal plan generation.
 */
class MealPlanViewModel(
    private val repository: RecipeRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<MealPlanUiState>(MealPlanUiState.Initial)
    val uiState: StateFlow<MealPlanUiState> = _uiState.asStateFlow()

    // Form state for custom meal plan
    private val _formState = MutableStateFlow(MealPlanFormState())
    val formState: StateFlow<MealPlanFormState> = _formState.asStateFlow()

    /**
     * Generate a custom meal plan based on user inputs.
     */
    fun generateCustomMealPlan() {
        viewModelScope.launch {
            _uiState.value = MealPlanUiState.Loading
            
            try {
                val form = _formState.value
                val request = MealPlanRequestDto(
                    days = form.days,
                    mealsPerDay = form.mealsPerDay,
                    nutritionGoals = if (form.useNutritionGoals) {
                        MealPlanNutritionGoalsDto(
                            calories = form.targetCalories,
                            protein = form.minProtein.takeIf { it > 0 },
                            fat = form.maxFat.takeIf { it > 0 },
                            sodium = form.maxSodium.takeIf { it > 0 }
                        )
                    } else null,
                    preferences = MealPlanPreferencesDto(
                        vegetarian = form.vegetarian.takeIf { it },
                        highProtein = form.highProtein.takeIf { it },
                        noDairy = form.dairyFree.takeIf { it },
                        noGluten = form.glutenFree.takeIf { it },
                        noNuts = form.noNuts.takeIf { it },
                        lowCarb = form.lowCarb.takeIf { it }
                    ),
                    varietyWeight = form.varietyWeight
                )
                
                val response = repository.createMealPlan(request)
                
                if (response != null) {
                    _uiState.value = MealPlanUiState.Success(response)
                } else {
                    _uiState.value = MealPlanUiState.Error("Failed to generate meal plan")
                }
            } catch (e: Exception) {
                _uiState.value = MealPlanUiState.Error(
                    e.message ?: "An error occurred while generating meal plan"
                )
            }
        }
    }

    /**
     * Generate meal plan from a preset using POST /api/meal-plan.
     * Presets are converted to proper request body format.
     */
    fun generateFromPreset(preset: MealPlanPreset) {
        viewModelScope.launch {
            _uiState.value = MealPlanUiState.Loading
            
            try {
                val request = MealPlanRequestDto(
                    days = preset.days,
                    mealsPerDay = 3,
                    preferences = MealPlanPreferencesDto(
                        vegetarian = if (preset == MealPlanPreset.VEGETARIAN) true else null,
                        highProtein = if (preset == MealPlanPreset.HIGH_PROTEIN) true else null,
                        lowCarb = if (preset == MealPlanPreset.LOW_CARB) true else null
                    ),
                    nutritionGoals = MealPlanNutritionGoalsDto(
                        calories = preset.calories,
                        protein = if (preset == MealPlanPreset.HIGH_PROTEIN) 150 else null
                    ),
                    varietyWeight = 0.7
                )
                
                val response = repository.createMealPlan(request)
                
                if (response != null) {
                    _uiState.value = MealPlanUiState.Success(response)
                } else {
                    _uiState.value = MealPlanUiState.Error("Failed to generate meal plan")
                }
            } catch (e: Exception) {
                _uiState.value = MealPlanUiState.Error(
                    e.message ?: "An error occurred while generating meal plan"
                )
            }
        }
    }

    // Form state update methods
    fun updateDays(days: Int) {
        _formState.value = _formState.value.copy(days = days.coerceIn(1, 7))
    }

    fun updateMealsPerDay(meals: Int) {
        _formState.value = _formState.value.copy(mealsPerDay = meals.coerceIn(2, 4))
    }

    fun updateTargetCalories(calories: Int) {
        _formState.value = _formState.value.copy(targetCalories = calories.coerceIn(1000, 5000))
    }

    fun updateMinProtein(protein: Int) {
        _formState.value = _formState.value.copy(minProtein = protein.coerceIn(0, 300))
    }

    fun updateMaxFat(fat: Int) {
        _formState.value = _formState.value.copy(maxFat = fat.coerceIn(0, 200))
    }

    fun updateMaxSodium(sodium: Int) {
        _formState.value = _formState.value.copy(maxSodium = sodium.coerceIn(0, 5000))
    }

    fun updateVarietyWeight(weight: Double) {
        _formState.value = _formState.value.copy(varietyWeight = weight.coerceIn(0.0, 1.0))
    }

    fun toggleNutritionGoals(enabled: Boolean) {
        _formState.value = _formState.value.copy(useNutritionGoals = enabled)
    }

    fun toggleVegetarian(enabled: Boolean) {
        _formState.value = _formState.value.copy(vegetarian = enabled)
    }

    fun toggleHighProtein(enabled: Boolean) {
        _formState.value = _formState.value.copy(highProtein = enabled)
    }

    fun toggleGlutenFree(enabled: Boolean) {
        _formState.value = _formState.value.copy(glutenFree = enabled)
    }

    fun toggleDairyFree(enabled: Boolean) {
        _formState.value = _formState.value.copy(dairyFree = enabled)
    }

    fun toggleNoNuts(enabled: Boolean) {
        _formState.value = _formState.value.copy(noNuts = enabled)
    }

    fun toggleLowCarb(enabled: Boolean) {
        _formState.value = _formState.value.copy(lowCarb = enabled)
    }

    fun resetForm() {
        _formState.value = MealPlanFormState()
        _uiState.value = MealPlanUiState.Initial
    }
    
    companion object {
        val Factory: ViewModelProvider.Factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return MealPlanViewModel(AppModule.recipeRepository) as T
            }
        }
    }
}

/**
 * UI state for meal plan feature.
 */
sealed class MealPlanUiState {
    object Initial : MealPlanUiState()
    object Loading : MealPlanUiState()
    
    data class Success(val mealPlan: MealPlanResponseDto) : MealPlanUiState()
    data class Error(val message: String) : MealPlanUiState()
}

/**
 * Form state for custom meal plan creation.
 * Matches the API request format for POST /api/meal-plan
 */
data class MealPlanFormState(
    val days: Int = 3,
    val mealsPerDay: Int = 3,
    val useNutritionGoals: Boolean = false,
    val targetCalories: Int = 2000,
    val minProtein: Int = 150,
    val maxFat: Int = 65,
    val maxSodium: Int = 2300,
    // Preferences matching API
    val vegetarian: Boolean = false,
    val highProtein: Boolean = false,
    val dairyFree: Boolean = false,
    val glutenFree: Boolean = false,
    val noNuts: Boolean = false,
    val lowCarb: Boolean = false,
    // Variety weight (0-1, higher = more variety)
    val varietyWeight: Double = 0.7
)

/**
 * Preset configurations for meal plans.
 * These presets are converted to POST /api/meal-plan requests.
 */
enum class MealPlanPreset(
    val displayName: String,
    val calories: Int,
    val days: Int,
    val emoji: String,
    val description: String
) {
    BALANCED(
        displayName = "Balanced",
        calories = 2000,
        days = 3,
        emoji = "⚖️",
        description = "Well-rounded nutrition for everyday health"
    ),
    VEGETARIAN(
        displayName = "Vegetarian",
        calories = 2000,
        days = 3,
        emoji = "🥗",
        description = "Plant-based with eggs and dairy"
    ),
    HIGH_PROTEIN(
        displayName = "High Protein",
        calories = 2200,
        days = 3,
        emoji = "💪",
        description = "Protein-rich meals for muscle building"
    ),
    LOW_CARB(
        displayName = "Low Carb",
        calories = 1800,
        days = 3,
        emoji = "🥑",
        description = "Reduced carbs for weight management"
    )
}
