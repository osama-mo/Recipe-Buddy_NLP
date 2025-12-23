package com.bassma.recipebuddy.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.SubcomposeAsyncImage
import coil.request.ImageRequest
import com.bassma.recipebuddy.domain.model.Recipe
import com.bassma.recipebuddy.ui.components.RecipeImageHelper
import com.bassma.recipebuddy.ui.components.common.ErrorState
import com.bassma.recipebuddy.ui.components.common.ShimmerBox
import com.bassma.recipebuddy.ui.components.detail.AnimatedCategoryChip
import com.bassma.recipebuddy.ui.components.detail.AnimatedDetailSection
import com.bassma.recipebuddy.ui.components.detail.AnimatedDirectionStep
import com.bassma.recipebuddy.ui.components.detail.AnimatedIngredientItem
import com.bassma.recipebuddy.ui.components.detail.NutritionCard
import com.bassma.recipebuddy.ui.components.detail.SimilarRecipesSection
import com.bassma.recipebuddy.ui.viewmodel.RecipeDetailViewModel
import com.bassma.recipebuddy.presentation.viewmodel.SimilarRecipesViewModel
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecipeDetailScreen(
    recipeId: String,
    onBackClick: () -> Unit,
    onSimilarRecipeClick: ((String) -> Unit)? = null,
    viewModel: RecipeDetailViewModel = viewModel(factory = RecipeDetailViewModel.Factory),
    similarRecipesViewModel: SimilarRecipesViewModel = viewModel(factory = SimilarRecipesViewModel.Factory)
) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()
    val similarRecipesState by similarRecipesViewModel.uiState.collectAsState()
    val scrollState = rememberScrollState()
    
    LaunchedEffect(recipeId) {
        viewModel.loadRecipe(recipeId)
        similarRecipesViewModel.loadSimilarRecipes(recipeId)
    }
    
    Box(modifier = Modifier.fillMaxSize()) {
        when {
            uiState.isLoading -> {
                DetailLoadingState()
            }
            uiState.error != null -> {
                ErrorState(
                    message = uiState.error!!,
                    onRetry = { viewModel.loadRecipe(recipeId) }
                )
            }
            uiState.recipe == null -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("🔍", fontSize = 48.sp)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Recipe not found")
                    }
                }
            }
            else -> {
                RecipeContent(
                    recipe = uiState.recipe!!,
                    scrollState = scrollState,
                    similarRecipesState = similarRecipesState,
                    onSimilarRecipeClick = onSimilarRecipeClick ?: {},
                    modifier = Modifier.fillMaxSize()
                )
            }
        }
        
        // Floating back button
        AnimatedVisibility(
            visible = true,
            enter = fadeIn() + scaleIn(),
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp)
                .statusBarsPadding()
        ) {
            FloatingActionButton(
                onClick = onBackClick,
                modifier = Modifier.size(48.dp),
                containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.9f),
                elevation = FloatingActionButtonDefaults.elevation(4.dp)
            ) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back",
                    tint = MaterialTheme.colorScheme.onSurface
                )
            }
        }
        
        // Share button
        uiState.recipe?.sourceUrl?.takeIf { it.isNotBlank() }?.let { url ->
            FloatingActionButton(
                onClick = {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                    context.startActivity(intent)
                },
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
                    .statusBarsPadding()
                    .size(48.dp),
                containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.9f),
                elevation = FloatingActionButtonDefaults.elevation(4.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Share,
                    contentDescription = "Open Original",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
private fun DetailLoadingState() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
    ) {
        ShimmerBox(
            modifier = Modifier
                .fillMaxWidth()
                .height(280.dp)
        )
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            ShimmerBox(modifier = Modifier.fillMaxWidth().height(32.dp))
            ShimmerBox(modifier = Modifier.fillMaxWidth(0.6f).height(24.dp))
            ShimmerBox(modifier = Modifier.fillMaxWidth().height(120.dp))
            ShimmerBox(modifier = Modifier.fillMaxWidth().height(200.dp))
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun RecipeContent(
    recipe: Recipe,
    scrollState: androidx.compose.foundation.ScrollState,
    similarRecipesState: com.bassma.recipebuddy.presentation.viewmodel.SimilarRecipesUiState,
    onSimilarRecipeClick: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    // Animation states
    var headerVisible by remember { mutableStateOf(false) }
    var contentVisible by remember { mutableStateOf(false) }
    
    LaunchedEffect(Unit) {
        headerVisible = true
        delay(200)
        contentVisible = true
    }
    
    Column(
        modifier = modifier.verticalScroll(scrollState)
    ) {
        // Hero Image with parallax effect
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(300.dp)
        ) {
            val imageUrl = remember(recipe.title) {
                RecipeImageHelper.getImageUrl(recipe.title, 800, 600)
            }
            
            SubcomposeAsyncImage(
                model = ImageRequest.Builder(LocalContext.current)
                    .data(imageUrl)
                    .crossfade(true)
                    .crossfade(600)
                    .build(),
                contentDescription = recipe.title,
                modifier = Modifier
                    .fillMaxSize()
                    .graphicsLayer {
                        // Parallax effect
                        translationY = scrollState.value * 0.5f
                    },
                contentScale = ContentScale.Crop,
                loading = {
                    ShimmerBox(modifier = Modifier.fillMaxSize())
                }
            )
            
            // Gradient overlay
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        brush = Brush.verticalGradient(
                            colors = listOf(
                                Color.Transparent,
                                Color.Black.copy(alpha = 0.3f),
                                Color.Black.copy(alpha = 0.8f)
                            ),
                            startY = 100f
                        )
                    )
            )
            
            // Title on image
            Box(
                modifier = Modifier
                    .align(Alignment.BottomStart)
                    .padding(20.dp)
            ) {
                val titleAlpha by animateFloatAsState(
                    targetValue = if (headerVisible) 1f else 0f,
                    animationSpec = tween(600),
                    label = "title_alpha"
                )
                val titleOffset by animateFloatAsState(
                    targetValue = if (headerVisible) 0f else 50f,
                    animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy),
                    label = "title_offset"
                )
                
                Column(
                    modifier = Modifier.graphicsLayer {
                        alpha = titleAlpha
                        translationY = titleOffset
                    }
                ) {
                    Text(
                        text = recipe.title,
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    
                    if (recipe.rating != null && recipe.rating > 0) {
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(text = "⭐", fontSize = 16.sp)
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = String.format("%.1f", recipe.rating),
                                style = MaterialTheme.typography.bodyLarge,
                                color = Color.White,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                }
            }
        }
        
        // Content section with animated cards
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Categories
            AnimatedVisibility(
                visible = contentVisible && recipe.categories.isNotEmpty(),
                enter = fadeIn(tween(400)) + slideInVertically(
                    initialOffsetY = { 30 },
                    animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy)
                )
            ) {
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    recipe.categories.forEachIndexed { index, category ->
                        AnimatedCategoryChip(
                            category = category,
                            delay = index * 50
                        )
                    }
                }
            }
            
            // Nutrition
            recipe.nutrition?.let { nutrition ->
                AnimatedDetailSection(
                    visible = contentVisible,
                    delay = 100
                ) {
                    NutritionCard(nutrition = nutrition)
                }
            }
            
            // Ingredients
            AnimatedDetailSection(
                visible = contentVisible,
                delay = 200
            ) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
                    )
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(text = "🥗", fontSize = 24.sp)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "Ingredients",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.weight(1f))
                            Surface(
                                shape = RoundedCornerShape(12.dp),
                                color = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)
                            ) {
                                Text(
                                    text = "${recipe.ingredients.size} items",
                                    style = MaterialTheme.typography.labelMedium,
                                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                                    color = MaterialTheme.colorScheme.primary
                                )
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        recipe.ingredients.forEachIndexed { index, ingredient ->
                            AnimatedIngredientItem(
                                ingredient = ingredient,
                                index = index,
                                visible = contentVisible
                            )
                        }
                    }
                }
            }
            
            // Directions
            AnimatedDetailSection(
                visible = contentVisible,
                delay = 300
            ) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.3f)
                    )
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(text = "👨‍🍳", fontSize = 24.sp)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "Directions",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        if (recipe.instructions.isEmpty()) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 16.dp),
                                horizontalArrangement = Arrangement.Center
                            ) {
                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    Text(text = "📝", fontSize = 32.sp)
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = "No directions available",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        } else {
                            recipe.instructions.forEachIndexed { index, instruction ->
                                AnimatedDirectionStep(
                                    step = index + 1,
                                    instruction = instruction,
                                    visible = contentVisible,
                                    delay = index * 80
                                )
                            }
                        }
                    }
                }
            }
            
            // Similar Recipes Section
            SimilarRecipesSection(
                uiState = similarRecipesState,
                onRecipeClick = onSimilarRecipeClick
            )
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
