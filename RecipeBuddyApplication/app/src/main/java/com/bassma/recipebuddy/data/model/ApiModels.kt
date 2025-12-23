package com.bassma.recipebuddy.data.model

import com.bassma.recipebuddy.domain.model.Nutrition
import com.bassma.recipebuddy.domain.model.Recipe
import com.google.gson.annotations.SerializedName

/**
 * API response models - Data Transfer Objects (DTOs)
 */

// Request DTOs
data class SearchRequestDto(
    @SerializedName("query")
    val query: String,
    @SerializedName("max_results")
    val maxResults: Int = 20,
    @SerializedName("page")
    val page: Int = 1
)

// Response DTOs
data class SearchResponseDto(
    @SerializedName("query")
    val query: String?,
    @SerializedName("parsed_query")
    val parsedQuery: ParsedQueryDto?,
    @SerializedName("results_count")
    val resultsCount: Int?,
    @SerializedName("page")
    val page: Int?,
    @SerializedName("per_page")
    val perPage: Int?,
    @SerializedName("has_next")
    val hasNext: Boolean?,
    @SerializedName("has_prev")
    val hasPrev: Boolean?,
    @SerializedName("query_time_ms")
    val queryTimeMs: Double?,
    @SerializedName("results")
    val results: List<RecipeResultDto>?
) {
    fun allRecipes(): List<RecipeResultDto> = results ?: emptyList()
    fun resultCount(): Int = resultsCount ?: allRecipes().size
    fun timeMs(): Long = queryTimeMs?.toLong() ?: 0L
    fun hasMorePages(): Boolean = hasNext ?: false
    fun currentPage(): Int = page ?: 1
}

data class ParsedQueryDto(
    @SerializedName("original_query")
    val originalQuery: String?,
    @SerializedName("corrected_query")
    val correctedQuery: String?,
    @SerializedName("spelling_corrections")
    val spellingCorrections: List<List<String>>?,
    @SerializedName("ingredients")
    val ingredients: List<String>?,
    @SerializedName("excluded_ingredients")
    val excludedIngredients: List<String>?,
    @SerializedName("categories")
    val categories: List<String>?,
    @SerializedName("dish_name")
    val dishName: String?,
    @SerializedName("meal_type")
    val mealType: String?,
    @SerializedName("nutrition")
    val nutrition: Map<String, Any>?
)

// Recipe result from search
data class RecipeResultDto(
    @SerializedName("id")
    val id: Int,
    @SerializedName("title")
    val title: String,
    @SerializedName("description")
    val description: String?,
    @SerializedName("categories")
    val categories: List<String>?,
    @SerializedName("ingredients")
    val ingredients: List<String>?,
    @SerializedName("score")
    val score: Double?,
    @SerializedName("semantic_score")
    val semanticScore: Double?,
    @SerializedName("rule_score")
    val ruleScore: Double?,
    @SerializedName("match_reasons")
    val matchReasons: List<String>?,
    @SerializedName("nutrition")
    val nutrition: NutritionDto?
)

// Recipe detail response (GET /recipe/{id})
data class RecipeDetailResponseDto(
    @SerializedName("id")
    val id: Int,
    @SerializedName("recipe")
    val recipe: RecipeDetailDto
)

data class RecipeDetailDto(
    @SerializedName("title")
    val title: String,
    @SerializedName("description")
    val description: String?,
    @SerializedName("categories")
    val categories: List<String>?,
    @SerializedName("ingredients")
    val ingredients: List<String>?,
    @SerializedName("directions")
    val directions: List<String>?,
    @SerializedName("nutrition")
    val nutrition: NutritionDto?,
    @SerializedName("rating")
    val rating: Double?
)

// Random recipes response
data class RandomRecipesResponseDto(
    @SerializedName("count")
    val count: Int,
    @SerializedName("recipes")
    val recipes: List<RandomRecipeDto>
)

data class RandomRecipeDto(
    @SerializedName("id")
    val id: Int,
    @SerializedName("title")
    val title: String,
    @SerializedName("categories")
    val categories: List<String>?,
    @SerializedName("calories")
    val calories: Double?,
    @SerializedName("protein")
    val protein: Double?
)

// Stats response
data class StatsResponseDto(
    @SerializedName("total_recipes")
    val totalRecipes: Int,
    @SerializedName("unique_categories")
    val uniqueCategories: Int?,
    @SerializedName("total_ingredients")
    val totalIngredients: Int?,
    @SerializedName("avg_ingredients_per_recipe")
    val avgIngredientsPerRecipe: Double?,
    @SerializedName("halal_compliant")
    val halalCompliant: Boolean?,
    @SerializedName("dataset_retention")
    val datasetRetention: String?
)

// Categories response
data class CategoriesResponseDto(
    @SerializedName("total_categories")
    val totalCategories: Int?,
    @SerializedName("categories")
    val categories: List<String>
)

// Ingredients response
data class IngredientsResponseDto(
    @SerializedName("total_ingredients")
    val totalIngredients: Int?,
    @SerializedName("ingredients")
    val ingredients: List<String>
)

// Health response
data class HealthResponseDto(
    @SerializedName("status")
    val status: String,
    @SerializedName("recipes_loaded")
    val recipesLoaded: Int?,
    @SerializedName("nlp_ready")
    val nlpReady: Boolean?,
    @SerializedName("matcher_ready")
    val matcherReady: Boolean?
)

// Nutrition DTO
data class NutritionDto(
    @SerializedName("calories")
    val calories: Double?,
    @SerializedName("protein")
    val protein: Double?,
    @SerializedName("fat")
    val fat: Double?,
    @SerializedName("sodium")
    val sodium: Double?
)

/**
 * Extension functions to map DTOs to domain models
 */

fun RecipeResultDto.toDomain(): Recipe {
    return Recipe(
        id = id.toString(),
        title = title,
        ingredients = ingredients ?: emptyList(),
        instructions = emptyList(), // Search results don't include directions
        categories = categories ?: emptyList(),
        imageUrl = null,
        sourceUrl = null,
        nutrition = nutrition?.toDomain(),
        prepTime = null,
        cookTime = null,
        servings = null,
        score = score ?: 0.0,
        description = description,
        matchReasons = matchReasons ?: emptyList()
    )
}

fun RecipeDetailDto.toDomain(id: Int): Recipe {
    return Recipe(
        id = id.toString(),
        title = title,
        ingredients = ingredients ?: emptyList(),
        instructions = directions ?: emptyList(),
        categories = categories ?: emptyList(),
        imageUrl = null,
        sourceUrl = null,
        nutrition = nutrition?.toDomain(),
        prepTime = null,
        cookTime = null,
        servings = null,
        score = 0.0,
        description = description,
        matchReasons = emptyList(),
        rating = rating
    )
}

fun RandomRecipeDto.toDomain(): Recipe {
    return Recipe(
        id = id.toString(),
        title = title,
        ingredients = emptyList(),
        instructions = emptyList(),
        categories = categories ?: emptyList(),
        imageUrl = null,
        sourceUrl = null,
        nutrition = if (calories != null || protein != null) {
            Nutrition(
                calories = calories ?: 0.0,
                protein = protein ?: 0.0,
                fat = 0.0,
                carbs = 0.0,
                fiber = null,
                sugar = null,
                sodium = null
            )
        } else null,
        prepTime = null,
        cookTime = null,
        servings = null,
        score = 0.0,
        description = null,
        matchReasons = emptyList()
    )
}

fun NutritionDto.toDomain(): Nutrition? {
    // Only return Nutrition if at least one value is present
    if (calories == null && protein == null && fat == null && sodium == null) {
        return null
    }
    return Nutrition(
        calories = calories ?: 0.0,
        protein = protein ?: 0.0,
        fat = fat ?: 0.0,
        carbs = 0.0,
        fiber = null,
        sugar = null,
        sodium = sodium
    )
}

fun List<RecipeResultDto>.toDomain(): List<Recipe> = map { it.toDomain() }

@JvmName("randomRecipesToDomain")
fun List<RandomRecipeDto>.toDomain(): List<Recipe> = map { it.toDomain() }

// ==================== Similar Recipes Feature ====================

data class SimilarRecipeDto(
    val id: String,
    val title: String,
    @SerializedName("image_url")
    val imageUrl: String?,
    @SerializedName("similarity_score")
    val similarityScore: Double,
    @SerializedName("similarity_reasons")
    val similarityReasons: List<String>,
    val ingredients: List<String>,
    val instructions: List<String>,
    @SerializedName("prep_time")
    val prepTime: String?,
    @SerializedName("cook_time")
    val cookTime: String?,
    val servings: Int?,
    val nutrition: NutritionDto?,
    val category: String?,
    val source: String?
)

data class SimilarRecipesResponseDto(
    @SerializedName("recipe_id")
    val recipeId: String,
    @SerializedName("similar_recipes")
    val similarRecipes: List<SimilarRecipeDto>,
    val count: Int
)

// ==================== Meal Plan Generator Feature ====================

/**
 * Request body for POST /api/meal-plan
 * 
 * Example:
 * {
 *     "days": 3,
 *     "meals_per_day": 3,
 *     "preferences": {"high_protein": true},
 *     "nutrition_goals": {"calories": 2200, "protein": 150}
 * }
 */
data class MealPlanRequestDto(
    val days: Int = 3,
    @SerializedName("meals_per_day")
    val mealsPerDay: Int = 3,
    val preferences: MealPlanPreferencesDto? = null,
    @SerializedName("nutrition_goals")
    val nutritionGoals: MealPlanNutritionGoalsDto? = null,
    @SerializedName("variety_weight")
    val varietyWeight: Double? = null
)

/**
 * Preferences for meal plan generation
 */
data class MealPlanPreferencesDto(
    val vegetarian: Boolean? = null,
    @SerializedName("high_protein")
    val highProtein: Boolean? = null,
    @SerializedName("no_dairy")
    val noDairy: Boolean? = null,
    @SerializedName("no_gluten")
    val noGluten: Boolean? = null,
    @SerializedName("no_nuts")
    val noNuts: Boolean? = null,
    @SerializedName("low_carb")
    val lowCarb: Boolean? = null
)

/**
 * Nutrition goals for meal plan (daily targets)
 */
data class MealPlanNutritionGoalsDto(
    val calories: Int? = null,
    val protein: Int? = null,
    val fat: Int? = null,
    val sodium: Int? = null
)

// Meal from meal plan - flat structure (not nested)
data class MealDto(
    val id: Int?,
    val title: String?,
    @SerializedName("desc")
    val description: String?,
    @SerializedName("meal_type")
    val mealType: String?,
    @SerializedName("meal_number")
    val mealNumber: Int?,
    val ingredients: List<String>?,
    val directions: List<String>?,
    val nutrition: MealNutritionDto?,
    val calories: Double?,
    val protein: Double?,
    val fat: Double?,
    val sodium: Double?,
    val sugar: Double?,
    val saturates: Double?,
    val categories: List<String>?
)

// Nutrition within meal
data class MealNutritionDto(
    val calories: Double?,
    val protein: Double?,
    val fat: Double?,
    val sodium: Double?,
    val sugar: Double?,
    val saturates: Double?
)

// Daily totals for a day plan
data class DailyTotalsDto(
    val calories: Double?,
    val protein: Double?,
    val fat: Double?,
    val carbs: Double?,
    val sodium: Double?,
    val sugar: Double?,
    val saturates: Double?
)

data class DayPlanDto(
    val day: Int?,
    val date: String?,
    val meals: List<MealDto>?,
    @SerializedName("daily_totals")
    val dailyTotals: DailyTotalsDto?
)

data class MealPlanPreferencesResponseDto(
    val diet: String?,
    @SerializedName("target_calories")
    val targetCalories: Int?,
    @SerializedName("protein_focus")
    val proteinFocus: Boolean?
)

data class MealPlanSummaryDto(
    @SerializedName("avg_calories_per_day")
    val avgCaloriesPerDay: Double?,
    @SerializedName("avg_protein_per_day")
    val avgProteinPerDay: Double?,
    @SerializedName("total_meals")
    val totalMeals: Int?,
    @SerializedName("total_days")
    val totalDays: Int?
)

data class MealPlanResponseDto(
    @SerializedName("meal_plan")
    val mealPlan: List<DayPlanDto>?,
    @SerializedName("nutrition_goals")
    val nutritionGoals: MealPlanNutritionGoalsDto?,
    val preferences: MealPlanPreferencesResponseDto?,
    val summary: MealPlanSummaryDto?,
    @SerializedName("generated_at")
    val generatedAt: String?
) {
    // Helper to get days (for backward compatibility)
    fun getDays(): List<DayPlanDto> = mealPlan ?: emptyList()
}

// ==================== Cache Stats Feature ====================

data class CacheEntryDto(
    val query: String,
    @SerializedName("result_count")
    val resultCount: Int,
    @SerializedName("cached_at")
    val cachedAt: String
)

data class CacheStatsDto(
    @SerializedName("total_entries")
    val totalEntries: Int,
    @SerializedName("total_cached_results")
    val totalCachedResults: Int,
    @SerializedName("cache_entries")
    val cacheEntries: List<CacheEntryDto>
)
