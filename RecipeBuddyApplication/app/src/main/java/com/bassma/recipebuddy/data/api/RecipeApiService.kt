package com.bassma.recipebuddy.data.api

import com.bassma.recipebuddy.data.model.CacheStatsDto
import com.bassma.recipebuddy.data.model.CategoriesResponseDto
import com.bassma.recipebuddy.data.model.HealthResponseDto
import com.bassma.recipebuddy.data.model.IngredientsResponseDto
import com.bassma.recipebuddy.data.model.MealPlanRequestDto
import com.bassma.recipebuddy.data.model.MealPlanResponseDto
import com.bassma.recipebuddy.data.model.RandomRecipesResponseDto
import com.bassma.recipebuddy.data.model.RecipeDetailResponseDto
import com.bassma.recipebuddy.data.model.SearchRequestDto
import com.bassma.recipebuddy.data.model.SearchResponseDto
import com.bassma.recipebuddy.data.model.SimilarRecipesResponseDto
import com.bassma.recipebuddy.data.model.StatsResponseDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * Retrofit API service interface for Recipe Buddy backend.
 * Base URL: Set in AppModule.kt (configure your own backend URL)
 */
interface RecipeApiService {
    
    /**
     * Health check endpoint.
     */
    @GET("health")
    suspend fun healthCheck(): Response<HealthResponseDto>
    
    /**
     * Get dataset statistics.
     */
    @GET("stats")
    suspend fun getStats(): Response<StatsResponseDto>
    
    /**
     * Main search with NLP query (POST).
     */
    @POST("search")
    suspend fun searchRecipes(
        @Body request: SearchRequestDto
    ): Response<SearchResponseDto>
    
    /**
     * Simple GET search with pagination.
     */
    @GET("search/simple")
    suspend fun searchRecipesSimple(
        @Query("q") query: String,
        @Query("limit") limit: Int = 20,
        @Query("page") page: Int = 1
    ): Response<SearchResponseDto>
    
    /**
     * Get a specific recipe by ID.
     */
    @GET("recipe/{id}")
    suspend fun getRecipeById(
        @Path("id") id: Int
    ): Response<RecipeDetailResponseDto>
    
    /**
     * Get random recipes.
     */
    @GET("random")
    suspend fun getRandomRecipes(
        @Query("count") count: Int = 5
    ): Response<RandomRecipesResponseDto>
    
    /**
     * Get all available categories.
     */
    @GET("categories")
    suspend fun getCategories(): Response<CategoriesResponseDto>
    
    /**
     * Get all available ingredients.
     */
    @GET("ingredients")
    suspend fun getIngredients(): Response<IngredientsResponseDto>
    
    // ==================== Similar Recipes Feature ====================
    
    /**
     * Get similar recipes to a specific recipe.
     * @param id Recipe ID to find similar recipes for
     * @param limit Maximum number of similar recipes to return (default: 5)
     * @param minScore Minimum similarity score threshold (default: 0.3)
     */
    @GET("api/recipes/{id}/similar")
    suspend fun getSimilarRecipes(
        @Path("id") id: String,
        @Query("limit") limit: Int = 5,
        @Query("min_score") minScore: Double = 0.3
    ): Response<SimilarRecipesResponseDto>
    
    // ==================== Meal Plan Generator Feature ====================
    
    /**
     * Generate a meal plan based on user preferences and nutrition goals.
     */
    @POST("api/meal-plan")
    suspend fun createMealPlan(
        @Body request: MealPlanRequestDto
    ): Response<MealPlanResponseDto>
    
    // ==================== Cache Stats Feature ====================
    
    /**
     * Get cache statistics and entries.
     */
    @GET("cache/stats")
    suspend fun getCacheStats(): Response<CacheStatsDto>
}
