<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Kotlin-1.9+-purple?style=for-the-badge&logo=kotlin&logoColor=white" alt="Kotlin">
  <img src="https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Jetpack_Compose-Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Android">
  <img src="https://img.shields.io/badge/spaCy-NLP-09A3D5?style=for-the-badge" alt="spaCy">
</p>

<h1 align="center">🍳 Recipe Buddy</h1>

<p align="center">
  <strong>Intelligent Halal Recipe Search powered by Natural Language Processing</strong>
</p>

<p align="center">
  An AI-powered recipe discovery platform that understands natural language queries like<br>
  <em>"high protein chicken without onion"</em> or <em>"low calorie vegetarian pasta"</em>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Backend Setup](#backend-setup)
  - [Android App Setup](#android-app-setup)
- [NLP Pipeline](#-nlp-pipeline)
- [API Documentation](#-api-documentation)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Recipe Buddy** is a full-stack intelligent recipe search system that combines:

- 🧠 **Natural Language Processing** - Understands complex queries with ingredients, exclusions, and nutrition requirements
- 📱 **Native Android App** - Beautiful Material 3 UI built with Jetpack Compose
- 🔍 **Smart Search** - TF-IDF based similarity matching with spell correction
- 🥗 **42,000+ Halal Recipes** - Pre-filtered dataset ensuring dietary compliance
- 📊 **Nutrition Tracking** - Filter by calories, protein, fat, and more

---

## ✨ Features

### 🔎 Intelligent Search
- Natural language query understanding
- Ingredient inclusion and exclusion (`"chicken without onion"`)
- Nutrition-based filtering (`"high protein"`, `"low calorie"`)
- Category and meal type detection (`"vegetarian breakfast"`)
- Automatic spell correction

### 🍽️ Meal Planning
- Generate personalized multi-day meal plans
- Quick presets: Balanced, Vegetarian, High Protein, Low Carb
- Customizable nutrition goals and dietary preferences
- Daily nutrition breakdown

### 🔗 Similar Recipes
- AI-powered recipe recommendations
- 70% ingredient similarity + 30% nutrition matching
- "More like this" discovery feature

### ⚡ Performance
- Intelligent caching (Redis/In-Memory)
- Optimized database queries
- Fast response times

### 📱 Modern Android App
- Jetpack Compose UI with Material 3
- Smooth animations and transitions
- Offline-friendly architecture
- Dark/Light theme support

---

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Android App   │ ◄─────► │   Flask API     │ ◄─────► │   PostgreSQL    │
│  (Kotlin/Compose)│   REST  │  (Python/spaCy) │   SQL   │  (42K Recipes)  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  NLP Pipeline │
                            │  • Tokenizer  │
                            │  • Parser     │
                            │  • Matcher    │
                            └───────────────┘
```

---

## 🛠️ Tech Stack

### Backend (`recipe_buddy_system/`)
| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core language |
| **Flask 3.0** | REST API framework |
| **spaCy** | NLP tokenization & processing |
| **scikit-learn** | TF-IDF similarity matching |
| **PostgreSQL** | Recipe database |
| **SQLAlchemy** | ORM |
| **Redis** | Caching (optional) |
| **Gunicorn** | Production server |

### Android App (`RecipeBuddyApplication/`)
| Technology | Purpose |
|------------|---------|
| **Kotlin** | Primary language |
| **Jetpack Compose** | Modern declarative UI |
| **Material 3** | Design system |
| **Retrofit** | HTTP client |
| **Coroutines** | Async operations |
| **ViewModel** | State management |

---

## 📁 Project Structure

```
Recipe-Buddy_NLP/
├── recipe_buddy_system/          # Backend API
│   ├── app.py                    # Flask application entry
│   ├── api/                      # API routes
│   │   ├── recipe_routes.py      # Recipe endpoints
│   │   ├── search_routes.py      # Search endpoints
│   │   └── system_routes.py      # Health & stats
│   ├── core/                     # Core logic
│   │   ├── query_parser.py       # NLP query parsing
│   │   ├── recipe_matcher.py     # Search & scoring
│   │   ├── similarity_engine.py  # TF-IDF similarity
│   │   ├── spell_corrector.py    # Typo correction
│   │   ├── meal_planner.py       # Meal plan generation
│   │   └── cache.py              # Caching layer
│   ├── config/                   # Configuration
│   │   ├── settings.py           # App settings
│   │   └── vocabulary.py         # NLP vocabularies
│   └── data/                     # Dataset info
│
└── RecipeBuddyApplication/       # Android App
    └── app/src/main/
        ├── java/.../recipebuddy/
        │   ├── data/             # Repository & API
        │   ├── domain/           # Use cases
        │   ├── presentation/     # ViewModels
        │   └── ui/               # Compose screens
        └── res/                  # Resources
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Android Studio (for mobile app)
- PostgreSQL (optional, can use JSON file)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Recipe-Buddy_NLP.git
   cd Recipe-Buddy_NLP/recipe_buddy_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Configure environment** (optional)
   ```bash
   # Create .env file for database connection
   echo "DATABASE_URL=postgresql://user:pass@host:5432/db" > .env
   ```

5. **Run the server**
   ```bash
   python app.py
   ```
   
   Server starts at: `http://localhost:5000`

### Android App Setup

1. **Open in Android Studio**
   ```
   Open: RecipeBuddyApplication/
   ```

2. **Configure backend URL**
   
   Edit `app/src/main/java/com/bassma/recipebuddy/di/AppModule.kt`:
   ```kotlin
   private const val BASE_URL = "http://YOUR_LOCAL_IP:5000/"
   ```
   
   > For emulator, use `http://10.0.2.2:5000/`

3. **Add Pixabay API key** (for recipe images)
   
   Get a free key at [pixabay.com/api/docs](https://pixabay.com/api/docs/) and update `RecipeImage.kt`

4. **Build and run**
   ```
   Click ▶️ Run in Android Studio
   ```

---

## 🧠 NLP Pipeline

The query processing follows a **5-stage pipeline**:

```
User Query: "high protein chicken without onion"
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Stage 1: Spell Correction              │
│  "chiken" → "chicken"                   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Stage 2: Tokenization (spaCy)          │
│  ["high", "protein", "chicken", ...]    │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Stage 3: Entity Extraction             │
│  ingredients: ["chicken"]               │
│  excluded: ["onion"]                    │
│  nutrition: {protein: {min: HIGH}}      │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Stage 4: Database Filtering            │
│  SQL queries with extracted entities    │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Stage 5: Scoring & Ranking             │
│  TF-IDF + Nutrition matching            │
└─────────────────────────────────────────┘
                    │
                    ▼
            Ranked Results
```

### Supported Query Patterns

| Pattern | Example |
|---------|---------|
| Include ingredients | `"chicken tomato pasta"` |
| Exclude ingredients | `"pasta without cheese"`, `"no onion"` |
| Nutrition goals | `"high protein"`, `"low calorie"` |
| Specific nutrition | `"at least 30g protein"` |
| Categories | `"vegetarian"`, `"indian"`, `"dessert"` |
| Meal types | `"breakfast"`, `"lunch"`, `"dinner"` |
| Combined | `"high protein vegetarian breakfast no eggs"` |

---

## 📡 API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API documentation |
| `GET` | `/health` | Health check |
| `GET` | `/stats` | Dataset statistics |
| `POST` | `/search` | Natural language search |
| `GET` | `/search/simple?q=...` | Simple query search |
| `GET` | `/recipe/<id>` | Get recipe by ID |
| `GET` | `/random` | Get random recipes |

### Advanced Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/recipes/<id>/similar` | Find similar recipes |
| `POST` | `/api/meal-plan` | Generate meal plan |
| `GET` | `/api/meal-plan/quick` | Quick meal plan presets |
| `GET` | `/api/cache/stats` | Cache statistics |

### Example Search Request

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "high protein chicken without onion", "limit": 10}'
```

<details>
<summary>📄 View Response</summary>

```json
{
  "query": {
    "original": "high protein chicken without onion",
    "ingredients": ["chicken"],
    "excluded_ingredients": ["onion"],
    "nutrition": {"protein": {"min": 20}}
  },
  "results": [
    {
      "id": 1234,
      "title": "Grilled Chicken Breast",
      "score": 0.95,
      "ingredients": ["chicken breast", "olive oil", "garlic"],
      "nutrition": {
        "calories": 280,
        "protein": 42,
        "fat": 8
      }
    }
  ],
  "total": 156,
  "returned": 10
}
```

</details>

---

## 📱 Screenshots



<p align="center">
  <img src="screenshots/home.jpeg" width="200" alt="Home Screen">
  <img src="screenshots/search.jpeg" width="200" alt="Search Results">
  <img src="screenshots/recipe.jpeg" width="200" alt="Recipe Detail">
  <img src="screenshots/meal-plan.jpeg" width="200" alt="Meal Planner">
</p>


---


## 🙏 Acknowledgments

- [spaCy](https://spacy.io/) - Industrial-strength NLP
- [scikit-learn](https://scikit-learn.org/) - Machine learning library
- [Jetpack Compose](https://developer.android.com/jetpack/compose) - Modern Android UI
- Recipe dataset contributors

---


<p align="center">
  <a href="#-recipe-buddy">Back to Top ⬆️</a>
</p>
