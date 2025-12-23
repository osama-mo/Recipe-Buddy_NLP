# Search walkthrough case 01

This folder is a reproducible, end-to-end walkthrough for **one search query** showing:

1. How the query is parsed (`core/query_parser.py`)
2. Which hard filters are applied in DB mode (`core/recipe_matcher.py::_search_database`)
3. How the v2_enhanced-style rule score is computed (`core/recipe_matcher.py::_calculate_recipe_score`)
4. Why the top results got the score they did

## Prerequisites

- Python env with project deps installed (see `requirements.txt`)
- A reachable PostgreSQL with the `recipes` table
- `DATABASE_URL` set (Railway/Neon/etc). Example (zsh):

```zsh
export DATABASE_URL='postgresql://USER:PASSWORD@HOST:PORT/DB?sslmode=require'
```

## Run

From repo root:

```zsh
python walkthroughs/search_case_01/run_case.py \
  --query "high protein chicken include tomato no onion" \
  --max-results 5
```

To capture a machine-readable artifact for your report:

```zsh
python walkthroughs/search_case_01/run_case.py \
  --query "high protein chicken include tomato no onion" \
  --max-results 5 \
  --json > walkthroughs/search_case_01/output.json
```

Optional:

```zsh
python walkthroughs/search_case_01/run_case.py --help
```

## What this prints

For the chosen query, the script prints:

- **Parsed query** fields: `dish_name`, `ingredients`, `excluded_ingredients`, `nutrition`, `categories`, `meal_type`
- **Hard-filter evaluation** for each returned recipe:
  - excluded ingredients check
  - nutrition constraints check
  - required-ingredient check (ALL required must be present)
  - dish-name check (if provided)
- **Score breakdown** using the same logic as `RecipeMatcher._calculate_recipe_score`:
  - dish-name contribution
  - per-ingredient contributions (title + search_text)
  - combo bonus
  - category/meal-type bonuses
  - nutrition “constraints met” bonus

The API returns a normalized score in `[0, 1]` via:

$$\text{normalized_score} = \frac{\text{rule_score (0..100)}}{100}$$

## Step-by-step pipeline (matches the running code)

### 1) Parse the query

Implemented in `core/query_parser.py` (`QueryParser.parse`).

Output shape (keys):

- `dish_name`: from `DISH_NAMES` substring match
- `ingredients`: from `COMMON_INGREDIENTS` substring match (with negation checks)
- `excluded_ingredients`: derived via regex negation patterns like `no X`, `without X`, `don't want X`
- `nutrition`: derived via numeric patterns and modifier phrases (e.g., `high protein` → `protein.min = 15`)
- `categories`, `meal_type`: keyword lookups

Important nuance: inclusion/exclusion depends on curated vocabulary lists, and results are truncated to at most 10 items each.

### 2) Apply DB hard filters (instant reject)

Implemented in `core/recipe_matcher.py` (`RecipeMatcher._search_database`). The order matters:

1. **Excluded ingredients**: recipes containing any excluded term are removed.
2. **Nutrition constraints**: recipes must have the nutrition column present and satisfy `min/max`.
3. **Required ingredients**: recipes must contain **ALL** required ingredients in title or `search_text`.
4. **Dish name** (optional): if a dish name is extracted, it must appear in title or `search_text`.

Only after passing all hard filters do recipes get scored.

### 3) Score valid recipes (0..100)

Implemented in `core/recipe_matcher.py` (`RecipeMatcher._calculate_recipe_score`). This walkthrough script reproduces the same logic and prints the component contributions:

- **Dish name match**: +20..+100 depending on where/how it matches.
- **Required ingredients**:
  - Ingredient in title: base + position bonus
  - Ingredient in `search_text`: +10
- **Combo bonus**: dish + ingredient(s) together in title (+20, plus optional proximity +10)
- **Category match**: +12 each (when present)
- **Meal type match**: +15 (when present)
- **Nutrition bonus**: +20 per nutrition constraint (if any constraints exist)

The API returns `score` normalized to `[0, 1]`.

## Notes / caveats

- This walkthrough is for **DB mode** (`USE_DATABASE=True`). If `DATABASE_URL` isn’t set, the main app can fall back to JSON mode, but this case is intended to mirror the production DB pipeline.
- The parser is **rule-based** (gazetteer + regex negation patterns) plus optional spell correction; it is not a trained NER model.

## Files

- `run_case.py`: prints the full step-by-step trace and score breakdown.
