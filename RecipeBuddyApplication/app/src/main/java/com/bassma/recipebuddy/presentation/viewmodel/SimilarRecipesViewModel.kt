package com.bassma.recipebuddy.presentation.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.bassma.recipebuddy.data.model.SimilarRecipeDto
import com.bassma.recipebuddy.di.AppModule
import com.bassma.recipebuddy.domain.repository.RecipeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for managing similar recipes feature.
 */
class SimilarRecipesViewModel(
    private val repository: RecipeRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<SimilarRecipesUiState>(SimilarRecipesUiState.Initial)
    val uiState: StateFlow<SimilarRecipesUiState> = _uiState.asStateFlow()

    fun loadSimilarRecipes(recipeId: String, limit: Int = 5, minScore: Double = 0.3) {
        viewModelScope.launch {
            _uiState.value = SimilarRecipesUiState.Loading
            
            try {
                val response = repository.getSimilarRecipes(recipeId, limit, minScore)
                
                if (response != null && response.similarRecipes.isNotEmpty()) {
                    _uiState.value = SimilarRecipesUiState.Success(
                        recipeId = response.recipeId,
                        similarRecipes = response.similarRecipes,
                        count = response.count
                    )
                } else {
                    _uiState.value = SimilarRecipesUiState.Empty
                }
            } catch (e: Exception) {
                _uiState.value = SimilarRecipesUiState.Error(
                    message = e.message ?: "Failed to load similar recipes"
                )
            }
        }
    }

    fun reset() {
        _uiState.value = SimilarRecipesUiState.Initial
    }
    
    companion object {
        val Factory: ViewModelProvider.Factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return SimilarRecipesViewModel(AppModule.recipeRepository) as T
            }
        }
    }
}

/**
 * UI state for similar recipes feature.
 */
sealed class SimilarRecipesUiState {
    object Initial : SimilarRecipesUiState()
    object Loading : SimilarRecipesUiState()
    object Empty : SimilarRecipesUiState()
    
    data class Success(
        val recipeId: String,
        val similarRecipes: List<SimilarRecipeDto>,
        val count: Int
    ) : SimilarRecipesUiState()
    
    data class Error(val message: String) : SimilarRecipesUiState()
}
