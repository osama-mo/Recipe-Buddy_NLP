package com.bassma.recipebuddy.domain.model

/**
 * Domain model representing a Recipe.
 * This is the core model used throughout the app.
 */
data class Recipe(
    val id: String,
    val title: String,
    val description: String? = null,
    val ingredients: List<String>,
    val instructions: List<String>,
    val categories: List<String>,
    val imageUrl: String? = null,
    val sourceUrl: String? = null,
    val nutrition: Nutrition? = null,
    val prepTime: Int? = null,
    val cookTime: Int? = null,
    val servings: Int? = null,
    val score: Double = 0.0,
    val matchReasons: List<String> = emptyList(),
    val rating: Double? = null
)

data class Nutrition(
    val calories: Double,
    val protein: Double,
    val fat: Double,
    val carbs: Double,
    val fiber: Double?,
    val sugar: Double?,
    val sodium: Double?
)
