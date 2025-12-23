package com.bassma.recipebuddy.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.SubcomposeAsyncImage
import coil.request.ImageRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.URL
import java.net.URLEncoder
import kotlin.math.abs

/**
 * Generates food images using Pixabay API (free, no API key limit for reasonable use).
 * Falls back to curated images if API fails.
 */
object RecipeImageHelper {
    
    // Pixabay API key (free to obtain at pixabay.com/api/docs/)
    // Get your free API key at: https://pixabay.com/api/docs/
    private const val PIXABAY_API_KEY = "YOUR_PIXABAY_API_KEY"
    
    // Cache for API results to avoid repeated calls
    private val imageCache = mutableMapOf<String, String>()
    
    /**
     * Get image URL using Pixabay search API.
     * Returns a direct image URL that can be displayed.
     */
    suspend fun searchImageUrl(query: String): String? {
        return withContext(Dispatchers.IO) {
            try {
                // Check cache first
                imageCache[query]?.let { return@withContext it }
                
                val searchQuery = extractSearchTerms(query)
                val encodedQuery = URLEncoder.encode("$searchQuery food", "UTF-8")
                val apiUrl = "https://pixabay.com/api/?key=$PIXABAY_API_KEY&q=$encodedQuery&image_type=photo&category=food&per_page=3&safesearch=true"
                
                val response = URL(apiUrl).readText()
                val json = JSONObject(response)
                val hits = json.getJSONArray("hits")
                
                if (hits.length() > 0) {
                    // Get the first result's medium-sized image
                    val imageUrl = hits.getJSONObject(0).getString("webformatURL")
                    imageCache[query] = imageUrl
                    imageUrl
                } else {
                    null
                }
            } catch (e: Exception) {
                e.printStackTrace()
                null
            }
        }
    }
    
    /**
     * Extract meaningful search terms from recipe title.
     */
    private fun extractSearchTerms(title: String): String {
        val stopWords = setOf("with", "and", "the", "a", "an", "in", "on", "for", "of", "to", "recipe", "style", "easy", "quick", "best", "homemade")
        val words = title.lowercase()
            .replace(Regex("[^a-z\\s]"), "")
            .split("\\s+".toRegex())
            .filter { it.length > 2 && it !in stopWords }
            .take(3)
        
        return words.joinToString(" ")
    }
    
    /**
     * Synchronous fallback - get a food image URL based on recipe title keywords.
     * Uses pre-defined Pexels images for reliability when API is not used.
     */
    fun getImageUrl(recipeTitle: String, width: Int = 400, height: Int = 300): String {
        val titleLower = recipeTitle.lowercase()
        
        // Find matching food category
        for ((keyword, urls) in foodImageUrls) {
            if (titleLower.contains(keyword)) {
                val index = abs(recipeTitle.hashCode()) % urls.size
                val baseUrl = urls[index]
                return "$baseUrl?auto=compress&cs=tinysrgb&w=$width&h=$height&fit=crop"
            }
        }
        
        // Fallback to default food images
        val index = abs(recipeTitle.hashCode()) % defaultFoodImages.size
        return "${defaultFoodImages[index]}?auto=compress&cs=tinysrgb&w=$width&h=$height&fit=crop"
    }
    
    // Pre-defined fallback images
    private val foodImageUrls = mapOf(
        "chicken" to listOf(
            "https://images.pexels.com/photos/2338407/pexels-photo-2338407.jpeg",
            "https://images.pexels.com/photos/6210876/pexels-photo-6210876.jpeg"
        ),
        "beef" to listOf(
            "https://images.pexels.com/photos/1639557/pexels-photo-1639557.jpeg",
            "https://images.pexels.com/photos/3535383/pexels-photo-3535383.jpeg"
        ),
        "lamb" to listOf(
            "https://images.pexels.com/photos/6542791/pexels-photo-6542791.jpeg"
        ),
        "fish" to listOf(
            "https://images.pexels.com/photos/3763847/pexels-photo-3763847.jpeg"
        ),
        "salmon" to listOf(
            "https://images.pexels.com/photos/3655916/pexels-photo-3655916.jpeg"
        ),
        "pasta" to listOf(
            "https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg"
        ),
        "rice" to listOf(
            "https://images.pexels.com/photos/723198/pexels-photo-723198.jpeg"
        ),
        "curry" to listOf(
            "https://images.pexels.com/photos/2474661/pexels-photo-2474661.jpeg"
        ),
        "soup" to listOf(
            "https://images.pexels.com/photos/1703272/pexels-photo-1703272.jpeg"
        ),
        "salad" to listOf(
            "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"
        ),
        "pizza" to listOf(
            "https://images.pexels.com/photos/315755/pexels-photo-315755.jpeg"
        ),
        "burger" to listOf(
            "https://images.pexels.com/photos/1639557/pexels-photo-1639557.jpeg"
        ),
        "cake" to listOf(
            "https://images.pexels.com/photos/291528/pexels-photo-291528.jpeg"
        ),
        "biryani" to listOf(
            "https://images.pexels.com/photos/7625056/pexels-photo-7625056.jpeg"
        ),
        "kebab" to listOf(
            "https://images.pexels.com/photos/2233729/pexels-photo-2233729.jpeg"
        ),
        "fried" to listOf(
            "https://images.pexels.com/photos/60616/fried-chicken-chicken-fried-crunchy-60616.jpeg"
        ),
        "grilled" to listOf(
            "https://images.pexels.com/photos/1268549/pexels-photo-1268549.jpeg"
        )
    )
    
    private val defaultFoodImages = listOf(
        "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg",
        "https://images.pexels.com/photos/1279330/pexels-photo-1279330.jpeg",
        "https://images.pexels.com/photos/376464/pexels-photo-376464.jpeg"
    )
}

/**
 * Recipe image that searches Pixabay API for relevant food images.
 * Falls back to keyword-based images if API fails.
 */
@Composable
fun RecipeImage(
    recipeTitle: String,
    modifier: Modifier = Modifier,
    height: Dp = 180.dp,
    cornerRadius: Dp = 16.dp
) {
    // State for the image URL - starts with fallback, updates when API returns
    var imageUrl by remember(recipeTitle) { 
        mutableStateOf(RecipeImageHelper.getImageUrl(recipeTitle)) 
    }
    var hasSearched by remember(recipeTitle) { mutableStateOf(false) }
    
    // Search Pixabay API for a better image
    LaunchedEffect(recipeTitle) {
        if (!hasSearched) {
            hasSearched = true
            val searchResult = RecipeImageHelper.searchImageUrl(recipeTitle)
            if (searchResult != null) {
                imageUrl = searchResult
            }
        }
    }
    
    SubcomposeAsyncImage(
        model = ImageRequest.Builder(LocalContext.current)
            .data(imageUrl)
            .crossfade(true)
            .crossfade(500)
            .build(),
        contentDescription = recipeTitle,
        modifier = modifier
            .fillMaxWidth()
            .height(height)
            .clip(RoundedCornerShape(cornerRadius)),
        contentScale = ContentScale.Crop,
        loading = {
            ShimmerBox(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(height)
            )
        },
        error = {
            FallbackFoodImage(
                title = recipeTitle,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(height)
            )
        }
    )
}

/**
 * Shimmer loading effect for images.
 */
@Composable
fun ShimmerBox(
    modifier: Modifier = Modifier
) {
    val shimmerColors = listOf(
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f),
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.2f),
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f)
    )
    
    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnim = transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = 1200,
                easing = FastOutSlowInEasing
            ),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer_translate"
    )
    
    val brush = Brush.linearGradient(
        colors = shimmerColors,
        start = Offset.Zero,
        end = Offset(x = translateAnim.value, y = translateAnim.value)
    )
    
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(brush)
    )
}

/**
 * Fallback image with gradient background when image fails to load.
 */
@Composable
fun FallbackFoodImage(
    title: String,
    modifier: Modifier = Modifier
) {
    val emoji = remember(title) {
        getFoodEmoji(title)
    }
    
    val gradientColors = remember {
        listOf(
            listOf(Color(0xFFFF6B6B), Color(0xFFFF8E53)),
            listOf(Color(0xFF4ECDC4), Color(0xFF44A08D)),
            listOf(Color(0xFFA8E6CF), Color(0xFF88D8B0)),
            listOf(Color(0xFFFFB347), Color(0xFFFFCC33)),
            listOf(Color(0xFF96CEB4), Color(0xFFFFC0CB))
        ).random()
    }
    
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(
                brush = Brush.linearGradient(gradientColors)
            ),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = emoji,
            fontSize = 48.sp
        )
    }
}

private fun getFoodEmoji(title: String): String {
    val titleLower = title.lowercase()
    return when {
        titleLower.contains("chicken") -> "🍗"
        titleLower.contains("beef") || titleLower.contains("steak") -> "🥩"
        titleLower.contains("fish") || titleLower.contains("salmon") -> "🐟"
        titleLower.contains("shrimp") || titleLower.contains("prawn") -> "🦐"
        titleLower.contains("pasta") || titleLower.contains("spaghetti") -> "🍝"
        titleLower.contains("pizza") -> "🍕"
        titleLower.contains("burger") -> "🍔"
        titleLower.contains("sandwich") -> "🥪"
        titleLower.contains("salad") -> "🥗"
        titleLower.contains("soup") -> "🍲"
        titleLower.contains("curry") -> "🍛"
        titleLower.contains("rice") -> "🍚"
        titleLower.contains("cake") -> "🎂"
        titleLower.contains("pie") -> "🥧"
        titleLower.contains("cookie") || titleLower.contains("biscuit") -> "🍪"
        titleLower.contains("bread") -> "🍞"
        titleLower.contains("egg") -> "🍳"
        titleLower.contains("breakfast") -> "🥞"
        titleLower.contains("dessert") || titleLower.contains("sweet") -> "🍰"
        titleLower.contains("drink") || titleLower.contains("smoothie") -> "🥤"
        titleLower.contains("ice cream") -> "🍨"
        titleLower.contains("fruit") -> "🍎"
        titleLower.contains("vegetable") || titleLower.contains("vegan") -> "🥬"
        else -> "🍽️"
    }
}
