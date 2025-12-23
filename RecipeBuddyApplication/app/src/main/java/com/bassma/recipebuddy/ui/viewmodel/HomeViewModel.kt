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
 * UI State for Home Screen
 */
data class HomeUiState(
    val isLoading: Boolean = true,
    val featuredRecipes: List<Recipe> = emptyList(),
    val categories: List<String> = emptyList(),
    val error: String? = null
)

/**
 * ViewModel for Home Screen
 */
class HomeViewModel(
    private val repository: RecipeRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
    
    init {
        loadInitialData()
    }
    
    private fun loadInitialData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            try {
                val featured = repository.getFeaturedRecipes(10)
                val categories = repository.getCategories()
                
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    featuredRecipes = featured,
                    categories = categories
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message ?: "Failed to load data"
                )
            }
        }
    }
    
    fun retry() {
        loadInitialData()
    }
    
    companion object {
        val Factory: ViewModelProvider.Factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return HomeViewModel(AppModule.recipeRepository) as T
            }
        }
    }
}
