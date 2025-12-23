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
 * UI State for Search Results Screen with pagination support
 */
data class SearchUiState(
    val isLoading: Boolean = false,
    val isLoadingMore: Boolean = false,
    val query: String = "",
    val recipes: List<Recipe> = emptyList(),
    val totalCount: Int = 0,
    val searchTimeMs: Long = 0,
    val currentPage: Int = 1,
    val hasNextPage: Boolean = false,
    val error: String? = null
)

private const val PAGE_SIZE = 15

/**
 * ViewModel for Search Results Screen with pagination
 */
class SearchViewModel(
    private val repository: RecipeRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SearchUiState())
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()
    
    fun search(query: String) {
        if (query.isBlank()) return
        
        viewModelScope.launch {
            _uiState.value = SearchUiState(
                isLoading = true,
                query = query
            )
            
            try {
                val result = repository.searchRecipes(query, limit = PAGE_SIZE, page = 1)
                
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    recipes = result.recipes,
                    totalCount = result.totalCount,
                    searchTimeMs = result.searchTimeMs,
                    currentPage = result.currentPage,
                    hasNextPage = result.hasNextPage
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message ?: "Search failed"
                )
            }
        }
    }
    
    fun loadNextPage() {
        val currentState = _uiState.value
        if (currentState.isLoadingMore || !currentState.hasNextPage) return
        
        viewModelScope.launch {
            _uiState.value = currentState.copy(isLoadingMore = true)
            
            try {
                val nextPage = currentState.currentPage + 1
                val result = repository.searchRecipes(
                    query = currentState.query,
                    limit = PAGE_SIZE,
                    page = nextPage
                )
                
                _uiState.value = _uiState.value.copy(
                    isLoadingMore = false,
                    recipes = currentState.recipes + result.recipes,
                    currentPage = result.currentPage,
                    hasNextPage = result.hasNextPage
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoadingMore = false,
                    error = e.message ?: "Failed to load more"
                )
            }
        }
    }
    
    fun clearSearch() {
        _uiState.value = SearchUiState()
    }
    
    companion object {
        val Factory: ViewModelProvider.Factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return SearchViewModel(AppModule.recipeRepository) as T
            }
        }
    }
}
