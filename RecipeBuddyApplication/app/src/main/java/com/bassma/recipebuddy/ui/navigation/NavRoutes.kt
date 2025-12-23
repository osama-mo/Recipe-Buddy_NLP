package com.bassma.recipebuddy.ui.navigation

/**
 * Navigation routes for the app
 */
sealed class NavRoutes(val route: String) {
    data object Home : NavRoutes("home")
    data object SearchResults : NavRoutes("search_results/{query}") {
        fun createRoute(query: String) = "search_results/$query"
    }
    data object RecipeDetail : NavRoutes("recipe_detail/{recipeId}") {
        fun createRoute(recipeId: String) = "recipe_detail/$recipeId"
    }
    data object MealPlan : NavRoutes("meal_plan")
    data object CacheStats : NavRoutes("cache_stats")
}
