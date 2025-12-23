# Halal Recipe Dataset

## Overview
This directory contains the halal-filtered recipe dataset used by the Recipe Buddy system.

## Files

### `halal_recipes.json` (Primary Dataset)
- **Size**: 42,787 recipes
- **Format**: JSON array of recipe objects
- **Compliance**: 100% halal-compliant
- **Retention**: 83.5% of original dataset

This is the **main dataset** to use in all applications. It has been pre-filtered to remove all non-halal ingredients.

### `recipes_with_nutritional_info.json` (Original Dataset)
- **Size**: 51,235 recipes
- **Format**: JSON array of recipe objects
- **Status**: Contains both halal and non-halal recipes
- **Usage**: Only for dataset creation/analysis

**⚠️ DO NOT USE THIS DIRECTLY IN APPLICATIONS**

## Creating the Halal Dataset

The halal dataset is created using `create_halal_dataset.py` in the root directory:

```bash
python create_halal_dataset.py
```

This script:
1. Loads `recipes_with_nutritional_info.json`
2. Filters out recipes containing non-halal ingredients
3. Saves the filtered dataset to `halal_recipes.json`

### Filtered Ingredients

The following non-halal ingredients are removed:

**Pork Products:**
- pork, bacon, ham, prosciutto, pancetta, sausage, chorizo
- pepperoni, salami, lard, fatback, guanciale, mortadella, coppa

**Alcohol:**
- wine, beer, vodka, rum, whiskey, bourbon, gin, tequila
- brandy, cognac, sherry, port, sake, champagne, prosecco
- vermouth, liqueur, mirin, cooking wine

**Non-Halal Gelatin:**
- gelatin, gelatine (unless halal-certified)

## Dataset Statistics

```
Original dataset:       51,235 recipes
Non-halal removed:      8,448 recipes (16.5%)
Halal dataset:          42,787 recipes (83.5% retention)
```

## Recipe Format

Each recipe in `halal_recipes.json` contains:

```json
{
  "title": "Recipe Name",
  "ingredients": [
    {"text": "ingredient 1"},
    {"text": "ingredient 2"}
  ],
  "instructions": "Step by step...",
  "nutrition": {
    "calories": 250.5,
    "protein": 12.3,
    "fat": 8.7,
    "sodium": 450.2
  },
  "categories": ["dinner", "chicken", "healthy"]
}
```

## Usage in Code

### Python (Recommended)

```python
import json

# Load halal recipes
with open('data/halal_recipes.json', 'r') as f:
    recipes = json.load(f)

print(f"Loaded {len(recipes)} halal recipes")

# Use with RecipeMatcher (no filtering needed)
from v2_enhanced.v2_recipe_matcher import RecipeMatcherV2

metadata = {'total_recipes': len(recipes)}
matcher = RecipeMatcherV2(recipes, metadata, halal_filter=False)
```

### Mobile (Android/Kotlin)

```kotlin
// Copy halal_recipes.json to app/src/main/assets/
val json = assets.open("halal_recipes.json").bufferedReader().use { it.readText() }
val recipes = Gson().fromJson(json, Array<Recipe>::class.java)

// All 42,787 recipes are halal-compliant - no runtime filtering needed
```

## Benefits of Pre-Filtered Dataset

✅ **No Runtime Filtering**: Faster app performance  
✅ **100% Halal Guaranteed**: Every recipe is verified  
✅ **Simpler Code**: No filtering logic needed  
✅ **Mobile-Friendly**: Ship clean dataset directly  
✅ **Offline-Ready**: Perfect for mobile apps  

## Updating the Dataset

If the original dataset (`recipes_with_nutritional_info.json`) is updated:

1. Run the creation script again:
   ```bash
   python create_halal_dataset.py
   ```

2. Review the filtering results

3. Replace the old `halal_recipes.json` with the new one

4. Update any applications using the dataset

## Verification

To verify the halal dataset has no non-halal ingredients:

```python
import json

with open('data/halal_recipes.json', 'r') as f:
    recipes = json.load(f)

# Check for common non-halal keywords
non_halal_keywords = ['bacon', 'pork', 'wine', 'beer', 'ham']

found = []
for recipe in recipes:
    title = recipe['title'].lower()
    for keyword in non_halal_keywords:
        if keyword in title:
            found.append((recipe['title'], keyword))

if found:
    print(f"⚠️  Found {len(found)} potential issues")
    for title, keyword in found[:5]:
        print(f"  - {title} ({keyword})")
else:
    print("✅ All recipes verified halal!")
```

## License & Attribution

This dataset is curated for the Recipe Buddy project. Original recipe data sources should be acknowledged according to their respective licenses.
