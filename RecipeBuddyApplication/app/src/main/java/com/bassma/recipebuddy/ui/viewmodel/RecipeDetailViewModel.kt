package com.bassma.recipebuddy.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.bassma.recipebuddy.di.AppModule
import com.bassma.recipebuddy.domain.model.Recipe
import com.bassma.recipebuddy.domain.repository.RecipeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * UI State for Recipe Detail Screen
 */
data class RecipeDetailUiState(
    val isLoading: Boolean = true,
    val recipe: Recipe? = null,
    val error: String? = null
)

/**
 * ViewModel for Recipe Detail Screen
 */
class RecipeDetailViewModel(
    private val repository: RecipeRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(RecipeDetailUiState())
    val uiState: StateFlow<RecipeDetailUiState> = _uiState.asStateFlow()
    
    fun loadRecipe(recipeId: String) {
        viewModelScope.launch {
            _uiState.value = RecipeDetailUiState(isLoading = true)
            
            try {
                val recipe = repository.getRecipeById(recipeId)
                
                _uiState.value = RecipeDetailUiState(
                    isLoading = false,
                    recipe = recipe,
                    error = if (recipe == null) "Recipe not found" else null
                )
            } catch (e: Exception) {
                _uiState.value = RecipeDetailUiState(
                    isLoading = false,
                    error = e.message ?: "Failed to load recipe"
                )
            }
        }
    }
    
    companion object {
        val Factory: ViewModelProvider.Factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return RecipeDetailViewModel(AppModule.recipeRepository) as T
            }
        }
    }
}
