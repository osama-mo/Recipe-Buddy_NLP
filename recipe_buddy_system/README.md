# Recipe Buddy API - Backend

Flask-based REST API for the Recipe Buddy intelligent recipe search system.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run the Server

```bash
python app.py
```

Server will start at: `http://localhost:5000`

---

## Base URL

**Local Development:**
```
http://localhost:5000
```

**For Android/Mobile (use your computer's local network IP):**
```
http://YOUR_LOCAL_IP:5000
```

---

# API Endpoints

## 1. Home / Documentation

### `GET /`

Returns API documentation and available endpoints.

**Request:**
```bash
curl http://localhost:5000/
```

**Response:**
```json
{
    "name": "Recipe Buddy API",
    "version": "2.0",
    "description": "Intelligent Halal Recipe Search with NLP and ML",
    "total_recipes": 42787,
    "endpoints": {
        "GET /": "This documentation",
        "GET /health": "Health check",
        "GET /stats": "Dataset statistics",
        "POST /search": "Search recipes with natural language query",
        "GET /search/simple": "Simple search with query parameter",
        "GET /recipe/<id>": "Get recipe by index",
        "GET /random": "Get random recipes",
        "GET /categories": "List all categories",
        "GET /ingredients": "List common ingredients",
        "POST /parse": "Parse query without searching"
    },
    "example_queries": [
        "chicken without onion",
        "low calorie vegetarian pasta",
        "spicy indian curry with coconut milk",
        "high protein breakfast no eggs"
    ]
}
```

---

## 2. Health Check

### `GET /health`

Check if the API is running and all components are ready.

**Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
    "status": "healthy",
    "recipes_loaded": 42787,
    "nlp_ready": true,
    "matcher_ready": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "healthy" if API is running |
| `recipes_loaded` | int | Number of recipes in database |
| `nlp_ready` | bool | NLP processor initialized |
| `matcher_ready` | bool | Recipe matcher initialized |

---

## 3. Search Recipes (POST)

### `POST /search`

Search recipes using natural language query with full NLP processing and spell correction.

**Request:**
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "chiken pasta without oniom",
    "max_results": 10,
    "use_tfidf": true
  }'
```

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Natural language search query |
| `max_results` | int | No | 20 | Maximum results to return (max: 100) |
| `use_tfidf` | bool | No | true | Use TF-IDF semantic matching |

**Response:**
```json
{
    "query": "chiken pasta without oniom",
    "parsed_query": {
        "original_query": "chiken pasta without oniom",
        "corrected_query": "chicken pasta without onion",
        "spelling_corrections": [
            ["chiken", "chicken"],
            ["oniom", "onion"]
        ],
        "ingredients": ["chicken"],
        "excluded_ingredients": ["onion", "onions", "onion powder"],
        "categories": ["pasta", "chicken", "italian"],
        "dish_name": "pasta",
        "meal_type": null,
        "nutrition": {}
    },
    "total_results": 10,
    "query_time_ms": 245.32,
    "results": [
        {
            "id": 39757,
            "title": "Campbell's 2 Step Creamy Chicken and Pasta",
            "description": "",
            "categories": [],
            "ingredients": [
                "chicken, broiler or fryers, breast, skinless, boneless, meat only, raw",
                "shortening, vegetable, household, composite",
                "soup, cream of chicken, canned, condensed",
                "water, bottled, generic"
            ],
            "score": 0.854,
            "semantic_score": 0.514,
            "rule_score": 1.0,
            "match_reasons": [
                "Matches 'pasta' dish type",
                "Contains: chicken",
                "Category: pasta, chicken"
            ],
            "nutrition": {
                "calories": null,
                "protein": null,
                "fat": null,
                "sodium": null
            }
        }
    ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Original query |
| `parsed_query` | object | NLP-parsed query components |
| `parsed_query.original_query` | string | Query before spell correction |
| `parsed_query.corrected_query` | string | Query after spell correction (null if no corrections) |
| `parsed_query.spelling_corrections` | array | List of [original, corrected] pairs |
| `parsed_query.ingredients` | array | Detected ingredients to include |
| `parsed_query.excluded_ingredients` | array | Ingredients to exclude (from "without", "no") |
| `parsed_query.categories` | array | Detected food categories |
| `parsed_query.dish_name` | string | Detected dish type |
| `parsed_query.meal_type` | string | Detected meal type (breakfast, lunch, etc.) |
| `parsed_query.nutrition` | object | Nutritional constraints |
| `total_results` | int | Number of results returned |
| `query_time_ms` | float | Query processing time in milliseconds |
| `results` | array | Array of matching recipes |

**Result Item Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Recipe ID (use with `/recipe/<id>`) |
| `title` | string | Recipe title |
| `description` | string | Recipe description |
| `categories` | array | Recipe categories |
| `ingredients` | array | First 10 ingredients |
| `score` | float | Combined match score (0-1) |
| `semantic_score` | float | TF-IDF similarity score (0-1) |
| `rule_score` | float | Rule-based match score (0-1) |
| `match_reasons` | array | Human-readable match explanations |
| `nutrition` | object | Nutritional information |

---

## 4. Simple Search (GET)

### `GET /search/simple`

Simple search using URL query parameters (easier for testing).

**Request:**
```bash
curl "http://localhost:5000/search/simple?q=spicy%20indian%20curry&limit=5"
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | ✅ Yes | - | Search query (URL encoded) |
| `limit` | int | No | 20 | Maximum results |

**Response:** Same format as `POST /search`

```json
{
    "query": "spicy indian curry",
    "total_results": 5,
    "query_time_ms": 156.79,
    "results": [
        {
            "id": 27361,
            "title": "Chapati for Indian Curry",
            "description": "",
            "categories": [],
            "ingredients": ["wheat flour", "water", "oil", "salt", "butter"],
            "score": 0.853,
            "semantic_score": 0.509,
            "rule_score": 1.0,
            "match_reasons": ["Matches 'curry' dish type", "Category: curry, indian"],
            "nutrition": {"calories": null, "protein": null, "fat": null, "sodium": null}
        }
    ]
}
```

---

## 5. Get Recipe by ID

### `GET /recipe/<id>`

Get complete recipe details by its ID.

**Request:**
```bash
curl http://localhost:5000/recipe/12556
```

**Response:**
```json
{
    "id": 12556,
    "recipe": {
        "title": "Indian Vegetable Curry",
        "description": null,
        "categories": [],
        "ingredients": [
            "spices, curry powder",
            "potatoes, raw, skin",
            "carrots, raw",
            "chickpeas (garbanzo beans, bengal gram), mature seeds, raw",
            "tomatoes, red, ripe, raw, year round average",
            "soup, chicken broth or bouillon, dry"
        ],
        "directions": [],
        "nutrition": {
            "calories": null,
            "protein": null,
            "fat": null,
            "sodium": null
        },
        "rating": null
    }
}
```

**Error Response (404):**
```json
{
    "error": "Recipe not found"
}
```

---

## 6. Random Recipes

### `GET /random`

Get random recipe suggestions (useful for homepage/discovery).

**Request:**
```bash
curl "http://localhost:5000/random?count=3"
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `count` | int | No | 5 | Number of random recipes (max: 50) |

**Response:**
```json
{
    "count": 3,
    "recipes": [
        {
            "id": 31057,
            "title": "Pizza dough (with yeast)",
            "categories": [],
            "calories": null,
            "protein": null
        },
        {
            "id": 41630,
            "title": "Fondant for Chocolate Cherries",
            "categories": [],
            "calories": null,
            "protein": null
        },
        {
            "id": 8234,
            "title": "Grilled Salmon with Herbs",
            "categories": [],
            "calories": null,
            "protein": null
        }
    ]
}
```

---

## 7. List Categories

### `GET /categories`

Get all available recipe categories with recipe counts.

**Request:**
```bash
curl http://localhost:5000/categories
```

**Response:**
```json
{
    "total_categories": 0,
    "categories": []
}
```

> Note: Categories may be empty if recipes don't have category tags in the dataset.

---

## 8. List Ingredients

### `GET /ingredients`

Get list of common ingredients recognized by the NLP system.

**Request:**
```bash
curl http://localhost:5000/ingredients
```

**Response:**
```json
{
    "total_ingredients": 127,
    "ingredients": [
        "chicken",
        "chicken breast",
        "chicken thigh",
        "beef",
        "ground beef",
        "steak",
        "lamb",
        "turkey",
        "fish",
        "salmon",
        "tuna",
        "shrimp",
        "tofu",
        "tomato",
        "onion",
        "garlic",
        "..."
    ]
}
```

---

## 9. Dataset Statistics

### `GET /stats`

Get statistics about the recipe dataset.

**Request:**
```bash
curl http://localhost:5000/stats
```

**Response:**
```json
{
    "total_recipes": 42787,
    "unique_categories": 0,
    "total_ingredients": 254553,
    "avg_ingredients_per_recipe": 5.9,
    "halal_compliant": true,
    "dataset_retention": "83.5%"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total_recipes` | int | Total recipes in database |
| `unique_categories` | int | Number of unique categories |
| `total_ingredients` | int | Sum of all ingredients across recipes |
| `avg_ingredients_per_recipe` | float | Average ingredients per recipe |
| `halal_compliant` | bool | Dataset is halal-filtered |
| `dataset_retention` | string | Percentage kept after halal filtering |

---

## 10. Parse Query (Debug)

### `POST /parse`

Parse a query without searching - useful for debugging NLP parsing.

**Request:**
```bash
curl -X POST http://localhost:5000/parse \
  -H "Content-Type: application/json" \
  -d '{"query": "low calorie vegetarian pasta without cheese"}'
```

**Response:**
```json
{
    "query": "low calorie vegetarian pasta without cheese",
    "parsed": {
        "original_query": "low calorie vegetarian pasta without cheese",
        "corrected_query": null,
        "spelling_corrections": [],
        "ingredients": [],
        "excluded_ingredients": ["cheese", "cheddar", "mozzarella", "parmesan", "feta", "cream cheese"],
        "categories": ["vegetarian", "low-carb", "pasta"],
        "dish_name": "pasta",
        "meal_type": null,
        "nutrition": {
            "calories": {"max": 300}
        }
    }
}
```

---

# Error Responses

All endpoints return errors in this format:

**400 Bad Request:**
```json
{
    "error": "Missing query parameter"
}
```

**404 Not Found:**
```json
{
    "error": "Recipe not found"
}
```

**500 Internal Server Error:**
```json
{
    "error": "Internal server error"
}
```

---

# Example Queries

The NLP system understands various query formats:

| Query | What It Extracts |
|-------|------------------|
| `chicken without onion` | ingredients: [chicken], excluded: [onion] |
| `low calorie vegetarian pasta` | categories: [vegetarian, pasta], nutrition: {calories: {max: 300}} |
| `spicy indian curry with coconut` | categories: [spicy, indian, curry], ingredients: [coconut] |
| `high protein breakfast no eggs` | meal_type: breakfast, nutrition: {protein: {min: 15}}, excluded: [eggs] |
| `quick easy dinner` | categories: [quick], meal_type: dinner |
| `gluten-free dessert` | categories: [gluten-free], meal_type: dessert |
| `chiken paasta` | Corrects to: "chicken pasta" |

---

# Jetpack Compose Integration

## Data Classes

```kotlin
// Request
data class SearchRequest(
    val query: String,
    val max_results: Int = 20,
    val use_tfidf: Boolean = true
)

// Responses
data class HealthResponse(
    val status: String,
    val recipes_loaded: Int,
    val nlp_ready: Boolean,
    val matcher_ready: Boolean
)

data class SearchResponse(
    val query: String,
    val parsed_query: ParsedQuery,
    val total_results: Int,
    val query_time_ms: Double,
    val results: List<RecipeResult>
)

data class ParsedQuery(
    val original_query: String,
    val corrected_query: String?,
    val spelling_corrections: List<List<String>>,
    val ingredients: List<String>,
    val excluded_ingredients: List<String>,
    val categories: List<String>,
    val dish_name: String?,
    val meal_type: String?,
    val nutrition: Map<String, Any>
)

data class RecipeResult(
    val id: Int,
    val title: String,
    val description: String,
    val categories: List<String>,
    val ingredients: List<String>,
    val score: Double,
    val semantic_score: Double,
    val rule_score: Double,
    val match_reasons: List<String>,
    val nutrition: Nutrition
)

data class Nutrition(
    val calories: Double?,
    val protein: Double?,
    val fat: Double?,
    val sodium: Double?
)

data class RecipeDetailResponse(
    val id: Int,
    val recipe: RecipeDetail
)

data class RecipeDetail(
    val title: String,
    val description: String?,
    val categories: List<String>,
    val ingredients: List<String>,
    val directions: List<String>,
    val nutrition: Nutrition,
    val rating: Double?
)

data class RandomResponse(
    val count: Int,
    val recipes: List<RandomRecipe>
)

data class RandomRecipe(
    val id: Int,
    val title: String,
    val categories: List<String>,
    val calories: Double?,
    val protein: Double?
)

data class StatsResponse(
    val total_recipes: Int,
    val unique_categories: Int,
    val total_ingredients: Int,
    val avg_ingredients_per_recipe: Double,
    val halal_compliant: Boolean,
    val dataset_retention: String
)
```

## Retrofit API Interface

```kotlin
interface RecipeBuddyApi {
    
    @GET("/")
    suspend fun getDocumentation(): Map<String, Any>
    
    @GET("/health")
    suspend fun healthCheck(): HealthResponse
    
    @GET("/stats")
    suspend fun getStats(): StatsResponse
    
    @POST("/search")
    suspend fun searchRecipes(@Body request: SearchRequest): SearchResponse
    
    @GET("/search/simple")
    suspend fun searchSimple(
        @Query("q") query: String,
        @Query("limit") limit: Int = 20
    ): SearchResponse
    
    @GET("/recipe/{id}")
    suspend fun getRecipe(@Path("id") id: Int): RecipeDetailResponse
    
    @GET("/random")
    suspend fun getRandomRecipes(@Query("count") count: Int = 5): RandomResponse
    
    @GET("/categories")
    suspend fun getCategories(): Map<String, Any>
    
    @GET("/ingredients")
    suspend fun getIngredients(): Map<String, Any>
    
    @POST("/parse")
    suspend fun parseQuery(@Body request: Map<String, String>): Map<String, Any>
}
```

## Retrofit Setup

```kotlin
object ApiClient {
    // Replace with your backend URL or local IP
    private const val BASE_URL = "http://YOUR_LOCAL_IP:5000/"
    
    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val api: RecipeBuddyApi = retrofit.create(RecipeBuddyApi::class.java)
}
```

## Usage Example

```kotlin
// In ViewModel
viewModelScope.launch {
    try {
        val response = ApiClient.api.searchRecipes(
            SearchRequest(query = "chicken pasta without onion")
        )
        _recipes.value = response.results
        _spellingCorrections.value = response.parsed_query.spelling_corrections
    } catch (e: Exception) {
        _error.value = e.message
    }
}
```

---

# Production Deployment

For production, use Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

# Dataset Info

- **Total Recipes:** 42,787
- **Halal Compliant:** Yes (pre-filtered)
- **Dataset Retention:** 83.5% from original 51,235 recipes
- **Average Ingredients:** 5.9 per recipe

---

## License

MIT License
