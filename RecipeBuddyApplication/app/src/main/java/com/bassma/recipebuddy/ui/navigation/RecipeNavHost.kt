package com.bassma.recipebuddy.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.bassma.recipebuddy.ui.screens.CacheStatsScreen
import com.bassma.recipebuddy.ui.screens.HomeScreen
import com.bassma.recipebuddy.ui.screens.MealPlanScreen
import com.bassma.recipebuddy.ui.screens.RecipeDetailScreen
import com.bassma.recipebuddy.ui.screens.SearchResultsScreen
import java.net.URLDecoder
import java.net.URLEncoder

@Composable
fun RecipeNavHost(
    navController: NavHostController
) {
    NavHost(
        navController = navController,
        startDestination = NavRoutes.Home.route
    ) {
        composable(NavRoutes.Home.route) {
            HomeScreen(
                onSearch = { query ->
                    val encodedQuery = URLEncoder.encode(query, "UTF-8")
                    navController.navigate(NavRoutes.SearchResults.createRoute(encodedQuery))
                },
                onMealPlanClick = {
                    navController.navigate(NavRoutes.MealPlan.route)
                },
                onCacheStatsClick = {
                    navController.navigate(NavRoutes.CacheStats.route)
                }
            )
        }
        
        composable(
            route = NavRoutes.SearchResults.route,
            arguments = listOf(navArgument("query") { type = NavType.StringType })
        ) { backStackEntry ->
            val query = backStackEntry.arguments?.getString("query") ?: ""
            val decodedQuery = URLDecoder.decode(query, "UTF-8")
            SearchResultsScreen(
                initialQuery = decodedQuery,
                onBackClick = { navController.popBackStack() },
                onRecipeClick = { recipeId ->
                    navController.navigate(NavRoutes.RecipeDetail.createRoute(recipeId))
                }
            )
        }
        
        composable(
            route = NavRoutes.RecipeDetail.route,
            arguments = listOf(navArgument("recipeId") { type = NavType.StringType })
        ) { backStackEntry ->
            val recipeId = backStackEntry.arguments?.getString("recipeId") ?: ""
            RecipeDetailScreen(
                recipeId = recipeId,
                onBackClick = { navController.popBackStack() },
                onSimilarRecipeClick = { similarRecipeId ->
                    navController.navigate(NavRoutes.RecipeDetail.createRoute(similarRecipeId))
                }
            )
        }
        
        composable(NavRoutes.MealPlan.route) {
            val mealPlanViewModel: com.bassma.recipebuddy.presentation.viewmodel.MealPlanViewModel = 
                androidx.lifecycle.viewmodel.compose.viewModel(
                    factory = com.bassma.recipebuddy.presentation.viewmodel.MealPlanViewModel.Factory
                )
            MealPlanScreen(
                viewModel = mealPlanViewModel,
                onRecipeClick = { recipeId ->
                    navController.navigate(NavRoutes.RecipeDetail.createRoute(recipeId))
                },
                onBackClick = { navController.popBackStack() }
            )
        }
        
        composable(NavRoutes.CacheStats.route) {
            val cacheStatsViewModel: com.bassma.recipebuddy.presentation.viewmodel.CacheStatsViewModel = 
                androidx.lifecycle.viewmodel.compose.viewModel(
                    factory = com.bassma.recipebuddy.presentation.viewmodel.CacheStatsViewModel.Factory
                )
            CacheStatsScreen(
                viewModel = cacheStatsViewModel,
                onBackClick = { navController.popBackStack() }
            )
        }
    }
}
