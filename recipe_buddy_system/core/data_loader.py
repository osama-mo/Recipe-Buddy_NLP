"""
Data Loader Module
Handles loading recipe data from PostgreSQL or JSON fallback
"""

import json
import gzip
import os
import gc
from typing import List, Dict, Any, Tuple, Optional

from config.settings import HALAL_RECIPES_PATH, USE_DATABASE


def load_recipes(path: str = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Load recipes from PostgreSQL database or JSON fallback.
    
    Returns:
        (recipes list, metadata dict)
    """
    if USE_DATABASE:
        return load_recipes_from_db()
    else:
        return load_recipes_from_json(path)


def load_recipes_from_db() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Load recipes from PostgreSQL database."""
    from core.models import get_session, Recipe
    from sqlalchemy import func
    
    print("Loading recipes from PostgreSQL database...")
    
    session = get_session()
    try:
        # Don't load all recipes - just get count
        # Recipes will be queried on-demand during searches
        count = session.query(func.count(Recipe.id)).scalar()
        
        metadata = {
            'total_recipes': count,
            'source': 'postgresql',
            'database': True,
            'lazy_load': True  # Recipes loaded on-demand
        }
        
        print(f"✅ Connected to database with {count:,} recipes (lazy-load mode)")
        
        # Return empty list - recipes will be queried on-demand
        return [], metadata
        
    finally:
        session.close()


def load_recipes_from_json(path: str = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Load recipes from JSON file (fallback)."""
    path = path or HALAL_RECIPES_PATH
    
    gz_path = path + '.gz' if not path.endswith('.gz') else path
    json_path = path[:-3] if path.endswith('.gz') else path
    
    actual_path = gz_path if os.path.exists(gz_path) else json_path
    
    if not os.path.exists(actual_path):
        raise FileNotFoundError(f"Recipe file not found: {path}")
    
    print(f"Loading recipes from JSON: {actual_path}")
    
    recipes = []
    
    if actual_path.endswith('.gz'):
        with gzip.open(actual_path, 'rt', encoding='utf-8') as f:
            raw_recipes = json.load(f)
    else:
        with open(actual_path, 'r', encoding='utf-8') as f:
            raw_recipes = json.load(f)
    
    for recipe in raw_recipes:
        processed = _preprocess_recipe(recipe)
        recipes.append(_slim_recipe(processed))
    
    del raw_recipes
    gc.collect()
    
    metadata = {
        'total_recipes': len(recipes),
        'source': actual_path,
        'database': False
    }
    
    print(f"✅ Loaded {len(recipes):,} recipes from JSON")
    
    return recipes, metadata


def get_recipe_by_id(recipe_id: int) -> Optional[Dict[str, Any]]:
    """Get full recipe by ID from database or cache."""
    if USE_DATABASE:
        from core.models import get_session, Recipe
        
        session = get_session()
        try:
            recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()
            return recipe.to_dict() if recipe else None
        finally:
            session.close()
    
    return None


def search_recipes_db(
    keywords: List[str] = None,
    excluded: List[str] = None,
    categories: List[str] = None,
    min_calories: float = None,
    max_calories: float = None,
    min_protein: float = None,
    max_protein: float = None,
    min_fat: float = None,
    max_fat: float = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search recipes directly in PostgreSQL.
    Much more efficient than loading all into memory.
    """
    if not USE_DATABASE:
        return []
    
    from core.models import get_session, Recipe
    from sqlalchemy import or_, and_, func
    
    session = get_session()
    try:
        query = session.query(Recipe)
        
        # Keyword search in title, ingredients, search_text
        if keywords:
            keyword_filters = []
            for kw in keywords:
                kw_lower = f"%{kw.lower()}%"
                keyword_filters.append(
                    or_(
                        func.lower(Recipe.title).like(kw_lower),
                        func.lower(Recipe.search_text).like(kw_lower),
                        Recipe.ingredients.any(func.lower(func.unnest(Recipe.ingredients)).like(kw_lower))
                    )
                )
            query = query.filter(and_(*keyword_filters))
        
        # Exclude ingredients
        if excluded:
            for exc in excluded:
                exc_lower = f"%{exc.lower()}%"
                query = query.filter(
                    ~func.lower(Recipe.search_text).like(exc_lower)
                )
        
        # Category filter
        if categories:
            cat_filters = []
            for cat in categories:
                cat_filters.append(Recipe.categories.any(cat))
            query = query.filter(or_(*cat_filters))
        
        # Nutrition filters
        if min_calories is not None:
            query = query.filter(Recipe.calories >= min_calories)
        if max_calories is not None:
            query = query.filter(Recipe.calories <= max_calories)
        if min_protein is not None:
            query = query.filter(Recipe.protein >= min_protein)
        if max_protein is not None:
            query = query.filter(Recipe.protein <= max_protein)
        if min_fat is not None:
            query = query.filter(Recipe.fat >= min_fat)
        if max_fat is not None:
            query = query.filter(Recipe.fat <= max_fat)
        
        # Execute and convert
        results = query.limit(limit).all()
        
        return [r.to_slim_dict() for r in results]
        
    finally:
        session.close()


def get_recipe_count() -> int:
    """Get total recipe count from database."""
    if USE_DATABASE:
        from core.models import get_session, Recipe
        
        session = get_session()
        try:
            return session.query(Recipe).count()
        finally:
            session.close()
    
    return 0


def _slim_recipe(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """Keep only essential fields for search."""
    return {
        'id': recipe.get('id', 0),
        'title': recipe.get('title', '')[:100],
        'desc': (recipe.get('desc', '') or '')[:150],
        'ingredients': (recipe.get('ingredients', []) or [])[:15],
        'directions': (recipe.get('directions', []) or [])[:5],
        'categories': (recipe.get('categories', []) or [])[:5],
        'calories': recipe.get('calories', 0),
        'protein': recipe.get('protein', 0),
        'fat': recipe.get('fat', 0),
        'sodium': recipe.get('sodium', 0),
        'sugar': recipe.get('sugar', 0),
        'saturates': recipe.get('saturates', 0),
    }


def _preprocess_recipe(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess a single recipe from JSON format."""
    processed = {}
    
    processed['id'] = recipe.get('id', 0)
    processed['title'] = recipe.get('title', '')
    processed['desc'] = recipe.get('desc', recipe.get('title', ''))
    processed['categories'] = recipe.get('categories', [])
    
    # Convert ingredients
    ingredients = recipe.get('ingredients', [])
    if ingredients:
        processed['ingredients'] = [
            ing['text'] if isinstance(ing, dict) else str(ing)
            for ing in ingredients
        ]
    else:
        processed['ingredients'] = []
    
    # Convert directions
    instructions = recipe.get('instructions', recipe.get('directions', []))
    if instructions:
        processed['directions'] = [
            inst['text'] if isinstance(inst, dict) else str(inst)
            for inst in instructions
        ]
    else:
        processed['directions'] = []
    
    # Extract nutrition
    nutr = recipe.get('nutr_values_per100g', {})
    if nutr:
        processed['calories'] = round(nutr.get('energy', 0), 1)
        processed['protein'] = round(nutr.get('protein', 0), 1)
        processed['fat'] = round(nutr.get('fat', 0), 1)
        processed['sodium'] = round(nutr.get('salt', 0) * 1000, 1)
        processed['sugar'] = round(nutr.get('sugars', 0), 1)
        processed['saturates'] = round(nutr.get('saturates', 0), 1)
    else:
        nutr_per_ing = recipe.get('nutr_per_ingredient', [])
        if nutr_per_ing:
            processed['calories'] = round(sum(n.get('nrg', 0) for n in nutr_per_ing), 1)
            processed['protein'] = round(sum(n.get('pro', 0) for n in nutr_per_ing), 1)
            processed['fat'] = round(sum(n.get('fat', 0) for n in nutr_per_ing), 1)
            processed['sodium'] = round(sum(n.get('sod', 0) for n in nutr_per_ing), 1)
            processed['sugar'] = round(sum(n.get('sug', 0) for n in nutr_per_ing), 1)
            processed['saturates'] = 0
        else:
            processed['calories'] = 0
            processed['protein'] = 0
            processed['fat'] = 0
            processed['sodium'] = 0
            processed['sugar'] = 0
            processed['saturates'] = 0
    
    # Combine quantity + unit + ingredient
    quantities = recipe.get('quantity', [])
    units = recipe.get('unit', [])
    if quantities and units and processed['ingredients']:
        enhanced = []
        for i, ing in enumerate(processed['ingredients']):
            qty = quantities[i]['text'] if i < len(quantities) and isinstance(quantities[i], dict) else ''
            unit = units[i]['text'] if i < len(units) and isinstance(units[i], dict) else ''
            if qty or unit:
                enhanced.append(f"{qty} {unit} {ing}".strip())
            else:
                enhanced.append(ing)
        processed['ingredients'] = enhanced
    
    return processed


def get_recipe_stats(recipes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics about the recipe dataset."""
    total = len(recipes)
    
    categories = set()
    for recipe in recipes:
        cats = recipe.get('categories', [])
        if isinstance(cats, list):
            categories.update(cats)
    
    total_ingredients = sum(len(recipe.get('ingredients', [])) for recipe in recipes)
    
    return {
        'total_recipes': total,
        'unique_categories': len(categories),
        'total_ingredients': total_ingredients,
        'avg_ingredients_per_recipe': round(total_ingredients / total, 1) if total > 0 else 0,
        'halal_compliant': True,
        'database_mode': USE_DATABASE
    }
