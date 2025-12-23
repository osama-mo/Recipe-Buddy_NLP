package com.bassma.recipebuddy.domain.repository

import com.bassma.recipebuddy.data.model.CacheStatsDto
import com.bassma.recipebuddy.data.model.MealPlanRequestDto
import com.bassma.recipebuddy.data.model.MealPlanResponseDto
import com.bassma.recipebuddy.data.model.SimilarRecipesResponseDto
import com.bassma.recipebuddy.domain.model.Recipe
import com.bassma.recipebuddy.domain.model.SearchResult

/**
 * Repository interface for recipe operations.
 * Defines the contract for data access.
 */
interface RecipeRepository {
    
    /**
     * Search recipes using natural language query with pagination.
     * The backend handles all NLP processing.
     */
    suspend fun searchRecipes(query: String, limit: Int = 20, page: Int = 1): SearchResult
    
    /**
     * Get a recipe by its ID.
     */
    suspend fun getRecipeById(id: String): Recipe?
    
    /**
     * Get random/featured recipes for home screen.
     */
    suspend fun getFeaturedRecipes(limit: Int = 10): List<Recipe>
    
    /**
     * Get recipe categories.
     */
    suspend fun getCategories(): List<String>
    
    /**
     * Get recipes by category.
     */
    suspend fun getRecipesByCategory(category: String, limit: Int = 50): List<Recipe>
    
    // ==================== Similar Recipes Feature ====================
    
    /**
     * Get similar recipes to a specific recipe.
     */
    suspend fun getSimilarRecipes(
        recipeId: String,
        limit: Int = 5,
        minScore: Double = 0.3
    ): SimilarRecipesResponseDto?
    
    // ==================== Meal Plan Generator Feature ====================
    
    /**
     * Generate a meal plan based on user preferences and nutrition goals.
     * Uses POST /api/meal-plan endpoint.
     */
    suspend fun createMealPlan(request: MealPlanRequestDto): MealPlanResponseDto?
    
    // ==================== Cache Stats Feature ====================
    
    /**
     * Get cache statistics and entries.
     */
    suspend fun getCacheStats(): CacheStatsDto?
}
