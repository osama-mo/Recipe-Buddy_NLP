package com.bassma.recipebuddy.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.bassma.recipebuddy.ui.components.common.EaseInOutQuad
import com.bassma.recipebuddy.ui.components.common.ErrorState
import com.bassma.recipebuddy.ui.components.common.ServerBootingScreen
import com.bassma.recipebuddy.ui.components.home.AnimatedSuggestionChip
import com.bassma.recipebuddy.ui.components.search.AnimatedSearchBar
import com.bassma.recipebuddy.ui.viewmodel.HomeViewModel
import kotlinx.coroutines.delay

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun HomeScreen(
    onSearch: (String) -> Unit,
    onMealPlanClick: () -> Unit = {},
    onCacheStatsClick: () -> Unit = {},
    viewModel: HomeViewModel = viewModel(factory = HomeViewModel.Factory)
) {
    val uiState by viewModel.uiState.collectAsState()
    var searchQuery by remember { mutableStateOf("") }
    
    // Animation states
    var titleVisible by remember { mutableStateOf(false) }
    var subtitleVisible by remember { mutableStateOf(false) }
    var searchBarVisible by remember { mutableStateOf(false) }
    var chipsVisible by remember { mutableStateOf(false) }
    
    // Trigger animations on launch
    LaunchedEffect(Unit) {
        titleVisible = true
        delay(200)
        subtitleVisible = true
        delay(200)
        searchBarVisible = true
        delay(300)
        chipsVisible = true
    }
    
    // Large pool of search suggestions
    val allQueries = remember {
        listOf(
            "🍗 chicken without onion",
            "🥗 low calorie vegetarian",
            "💪 high protein breakfast",
            "🌶️ spicy indian curry",
            "🍝 easy pasta recipes",
            "🥘 quick dinner ideas",
            "🍕 homemade pizza",
            "🥩 grilled steak",
            "🍜 ramen noodles",
            "🥙 healthy wraps",
            "🍲 comfort soup",
            "🥞 fluffy pancakes",
            "🍛 butter chicken",
            "🌮 soft tacos",
            "🥗 fresh salad",
            "🍳 perfect eggs",
            "🍔 juicy burgers",
            "🥐 french pastries",
            "🍰 chocolate cake",
            "🍪 crispy cookies",
            "🥖 artisan bread",
            "🍱 sushi rolls",
            "🥡 fried rice",
            "🌯 breakfast burrito",
            "🧆 falafel bowl",
            "🥨 soft pretzels",
            "🍩 glazed donuts",
            "🥧 apple pie",
            "🧁 vanilla cupcakes",
            "🍮 smooth pudding"
        )
    }
    
    // Pick 3 random queries on each composition
    var refreshKey by remember { mutableStateOf(0) }
    val exampleQueries = remember(refreshKey) {
        allQueries.shuffled().take(3)
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Animated App Title
            AnimatedVisibility(
                visible = titleVisible,
                enter = fadeIn(tween(600)) + slideInVertically(
                    initialOffsetY = { -50 },
                    animationSpec = spring(
                        dampingRatio = Spring.DampingRatioMediumBouncy,
                        stiffness = Spring.StiffnessLow
                    )
                )
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "🍳",
                        fontSize = 64.sp
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = "Recipe Buddy",
                        fontSize = 36.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Animated Subtitle
            AnimatedVisibility(
                visible = subtitleVisible,
                enter = fadeIn(tween(600)) + expandVertically()
            ) {
                Text(
                    text = "Discover delicious halal recipes\npowered by AI ✨",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                    textAlign = TextAlign.Center
                )
            }
            
            Spacer(modifier = Modifier.height(40.dp))
            
            // Animated Search Bar
            AnimatedVisibility(
                visible = searchBarVisible,
                enter = fadeIn(tween(500)) + scaleIn(
                    initialScale = 0.8f,
                    animationSpec = spring(
                        dampingRatio = Spring.DampingRatioMediumBouncy,
                        stiffness = Spring.StiffnessLow
                    )
                )
            ) {
                AnimatedSearchBar(
                    query = searchQuery,
                    onQueryChange = { searchQuery = it },
                    onSearch = {
                        if (searchQuery.isNotBlank()) {
                            onSearch(searchQuery)
                        }
                    }
                )
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // Animated suggestion chips
            AnimatedVisibility(
                visible = chipsVisible,
                enter = fadeIn(tween(500)) + slideInVertically(
                    initialOffsetY = { 50 },
                    animationSpec = spring(
                        dampingRatio = Spring.DampingRatioMediumBouncy,
                        stiffness = Spring.StiffnessLow
                    )
                )
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "✨ Try these searches",
                            style = MaterialTheme.typography.titleSmall,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                        TextButton(
                            onClick = {
                                refreshKey++
                            },
                            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Text(
                                text = "🔄 Refresh",
                                style = MaterialTheme.typography.labelSmall
                            )
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        exampleQueries.forEachIndexed { index, query ->
                            AnimatedSuggestionChip(
                                text = query,
                                delay = index * 100,
                                onClick = {
                                    searchQuery = query.substringAfter(" ")
                                    onSearch(query.substringAfter(" "))
                                }
                            )
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // Quick access buttons
            AnimatedVisibility(
                visible = chipsVisible,
                enter = fadeIn(tween(600, delayMillis = 400)) + slideInVertically(
                    initialOffsetY = { 50 },
                    animationSpec = spring(
                        dampingRatio = Spring.DampingRatioMediumBouncy,
                        stiffness = Spring.StiffnessLow
                    )
                )
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Meal Plan Button
                    Card(
                        modifier = Modifier
                            .weight(1f)
                            .clickable { onMealPlanClick() },
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.secondaryContainer
                        ),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.DateRange,
                                contentDescription = "Meal Plan",
                                modifier = Modifier.size(32.dp),
                                tint = MaterialTheme.colorScheme.onSecondaryContainer
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Meal Plan",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.SemiBold,
                                color = MaterialTheme.colorScheme.onSecondaryContainer
                            )
                            Text(
                                text = "Generator",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.7f)
                            )
                        }
                    }
                    
                    // Cache Stats Button
                    Card(
                        modifier = Modifier
                            .weight(1f)
                            .clickable { onCacheStatsClick() },
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.tertiaryContainer
                        ),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Info,
                                contentDescription = "Cache Stats",
                                modifier = Modifier.size(32.dp),
                                tint = MaterialTheme.colorScheme.onTertiaryContainer
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Cache Stats",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.SemiBold,
                                color = MaterialTheme.colorScheme.onTertiaryContainer
                            )
                            Text(
                                text = "Monitor",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onTertiaryContainer.copy(alpha = 0.7f)
                            )
                        }
                    }
                }
            }
            
            // Show error if any
            uiState.error?.let { error ->
                Spacer(modifier = Modifier.height(24.dp))
                AnimatedVisibility(
                    visible = true,
                    enter = fadeIn() + slideInVertically()
                ) {
                    ErrorState(
                        message = error,
                        onRetry = { viewModel.retry() }
                    )
                }
            }
        }
        
        // Loading Overlay - Server Booting Screen
        AnimatedVisibility(
            visible = uiState.isLoading,
            enter = fadeIn(),
            exit = fadeOut()
        ) {
            ServerBootingScreen()
        }
    }
}
