package com.bassma.recipebuddy.presentation.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.bassma.recipebuddy.data.model.CacheStatsDto
import com.bassma.recipebuddy.di.AppModule
import com.bassma.recipebuddy.domain.repository.RecipeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for managing cache statistics.
 */
class CacheStatsViewModel(
    private val repository: RecipeRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<CacheStatsUiState>(CacheStatsUiState.Initial)
    val uiState: StateFlow<CacheStatsUiState> = _uiState.asStateFlow()

    fun loadCacheStats() {
        viewModelScope.launch {
            _uiState.value = CacheStatsUiState.Loading
            
            try {
                val stats = repository.getCacheStats()
                
                if (stats != null) {
                    _uiState.value = CacheStatsUiState.Success(stats)
                } else {
                    _uiState.value = CacheStatsUiState.Error("Failed to load cache stats")
                }
            } catch (e: Exception) {
                _uiState.value = CacheStatsUiState.Error(
                    message = e.message ?: "An error occurred while loading cache stats"
                )
            }
        }
    }

    fun refresh() {
        loadCacheStats()
    }
    
    companion object {
        val Factory: ViewModelProvider.Factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return CacheStatsViewModel(AppModule.recipeRepository) as T
            }
        }
    }
}

/**
 * UI state for cache statistics.
 */
sealed class CacheStatsUiState {
    object Initial : CacheStatsUiState()
    object Loading : CacheStatsUiState()
    
    data class Success(val stats: CacheStatsDto) : CacheStatsUiState()
    data class Error(val message: String) : CacheStatsUiState()
}
