package com.bassma.recipebuddy.data.repository

import com.bassma.recipebuddy.data.api.RecipeApiService
import com.bassma.recipebuddy.data.model.CacheStatsDto
import com.bassma.recipebuddy.data.model.MealPlanRequestDto
import com.bassma.recipebuddy.data.model.MealPlanResponseDto
import com.bassma.recipebuddy.data.model.SearchRequestDto
import com.bassma.recipebuddy.data.model.SimilarRecipesResponseDto
import com.bassma.recipebuddy.data.model.toDomain
import com.bassma.recipebuddy.domain.model.Recipe
import com.bassma.recipebuddy.domain.model.SearchResult
import com.bassma.recipebuddy.domain.repository.RecipeRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Implementation of RecipeRepository using Retrofit API.
 */
class RecipeRepositoryImpl(
    private val apiService: RecipeApiService
) : RecipeRepository {
    
    override suspend fun searchRecipes(query: String, limit: Int, page: Int): SearchResult {
        return withContext(Dispatchers.IO) {
            val request = SearchRequestDto(query = query, maxResults = limit, page = page)
            val response = apiService.searchRecipes(request)
            
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                SearchResult(
                    recipes = dto.allRecipes().toDomain(),
                    totalCount = dto.resultCount(),
                    query = dto.query ?: query,
                    searchTimeMs = dto.timeMs(),
                    currentPage = dto.currentPage(),
                    hasNextPage = dto.hasMorePages()
                )
            } else {
                throw ApiException(
                    code = response.code(),
                    message = response.message() ?: "Unknown error"
                )
            }
        }
    }
    
    override suspend fun getRecipeById(id: String): Recipe? {
        return withContext(Dispatchers.IO) {
            val recipeId = id.toIntOrNull() ?: return@withContext null
            val response = apiService.getRecipeById(recipeId)
            
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                dto.recipe.toDomain(dto.id)
            } else if (response.code() == 404) {
                null
            } else {
                throw ApiException(
                    code = response.code(),
                    message = response.message() ?: "Unknown error"
                )
            }
        }
    }
    
    override suspend fun getFeaturedRecipes(limit: Int): List<Recipe> {
        return withContext(Dispatchers.IO) {
            val response = apiService.getRandomRecipes(limit)
            
            if (response.isSuccessful && response.body() != null) {
                response.body()!!.recipes.toDomain()
            } else {
                throw ApiException(
                    code = response.code(),
                    message = response.message() ?: "Unknown error"
                )
            }
        }
    }
    
    override suspend fun getCategories(): List<String> {
        return withContext(Dispatchers.IO) {
            val response = apiService.getCategories()
            
            if (response.isSuccessful && response.body() != null) {
                response.body()!!.categories
            } else {
                throw ApiException(
                    code = response.code(),
                    message = response.message() ?: "Unknown error"
                )
            }
        }
    }
    
    override suspend fun getRecipesByCategory(category: String, limit: Int): List<Recipe> {
        // Use search with category as query since there's no dedicated endpoint
        return withContext(Dispatchers.IO) {
            val request = SearchRequestDto(query = category, maxResults = limit)
            val response = apiService.searchRecipes(request)
            
            if (response.isSuccessful && response.body() != null) {
                response.body()!!.allRecipes().toDomain()
            } else {
                throw ApiException(
                    code = response.code(),
                    message = response.message() ?: "Unknown error"
                )
            }
        }
    }
    
    // ==================== Similar Recipes Feature ====================
    
    override suspend fun getSimilarRecipes(
        recipeId: String,
        limit: Int,
        minScore: Double
    ): SimilarRecipesResponseDto? {
        return withContext(Dispatchers.IO) {
            val response = apiService.getSimilarRecipes(recipeId, limit, minScore)
            
            if (response.isSuccessful) {
                response.body()
            } else if (response.code() == 404) {
                null
            } else {
                throw ApiException(
                    code = response.code(),
                    message = response.message() ?: "Unknown error"
                )
            }
        }
    }
    
    // ==================== Meal Plan Generator Feature ====================
    
    override suspend fun createMealPlan(request: MealPlanRequestDto): MealPlanResponseDto? {
        return withContext(Dispatchers.IO) {
            val response = apiService.createMealPlan(request)
            
            if (response.isSuccessful) {
                response.body()
            } else {
                throw ApiException(
                    code = response.code(),
                    message = response.message() ?: "Unknown error"
                )
            }
        }
    }
    
    // ==================== Cache Stats Feature ====================
    
    override suspend fun getCacheStats(): CacheStatsDto? {
        return withContext(Dispatchers.IO) {
            val response = apiService.getCacheStats()
            
            if (response.isSuccessful) {
                response.body()
            } else {
                throw ApiException(
                    code = response.code(),
                    message = response.message() ?: "Unknown error"
                )
            }
        }
    }
}

/**
 * Custom exception for API errors.
 */
class ApiException(
    val code: Int,
    override val message: String
) : Exception(message)
