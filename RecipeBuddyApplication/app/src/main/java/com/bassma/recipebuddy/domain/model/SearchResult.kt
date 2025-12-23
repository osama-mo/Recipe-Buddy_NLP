package com.bassma.recipebuddy.domain.model

/**
 * Search result containing recipes and pagination metadata.
 */
data class SearchResult(
    val recipes: List<Recipe>,
    val totalCount: Int,
    val query: String,
    val searchTimeMs: Long,
    val currentPage: Int = 1,
    val hasNextPage: Boolean = false
)
