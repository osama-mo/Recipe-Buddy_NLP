#!/usr/bin/env python3
"""
Migration Script: Load recipes from JSON into PostgreSQL (Neon)

Usage:
    1. Set DATABASE_URL environment variable
    2. Run: python migrate_to_postgres.py

This script:
    1. Creates database tables
    2. Loads recipes from halal_recipes.json.gz
    3. Preprocesses and inserts into PostgreSQL
    4. Creates search indexes
"""

import json
import gzip
import os
import sys
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.models import Recipe, Base, get_engine, get_session


def preprocess_recipe(recipe: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """Convert JSON recipe to database format."""
    
    # Extract ingredients
    ingredients = recipe.get('ingredients', [])
    if ingredients:
        ingredients = [
            ing['text'] if isinstance(ing, dict) else str(ing)
            for ing in ingredients
        ]
    
    # Combine with quantity and unit
    quantities = recipe.get('quantity', [])
    units = recipe.get('unit', [])
    if quantities and units and ingredients:
        enhanced = []
        for i, ing in enumerate(ingredients):
            qty = quantities[i]['text'] if i < len(quantities) and isinstance(quantities[i], dict) else ''
            unit = units[i]['text'] if i < len(units) and isinstance(units[i], dict) else ''
            if qty or unit:
                enhanced.append(f"{qty} {unit} {ing}".strip())
            else:
                enhanced.append(ing)
        ingredients = enhanced
    
    # Extract directions
    directions = recipe.get('instructions', recipe.get('directions', []))
    if directions:
        directions = [
            d['text'] if isinstance(d, dict) else str(d)
            for d in directions
        ]
    
    # Extract nutrition
    nutr = recipe.get('nutr_values_per100g', {})
    if nutr:
        calories = round(nutr.get('energy', 0), 1)
        protein = round(nutr.get('protein', 0), 1)
        fat = round(nutr.get('fat', 0), 1)
        sodium = round(nutr.get('salt', 0) * 1000, 1)
        sugar = round(nutr.get('sugars', 0), 1)
        saturates = round(nutr.get('saturates', 0), 1)
    else:
        nutr_per_ing = recipe.get('nutr_per_ingredient', [])
        if nutr_per_ing:
            calories = round(sum(n.get('nrg', 0) for n in nutr_per_ing), 1)
            protein = round(sum(n.get('pro', 0) for n in nutr_per_ing), 1)
            fat = round(sum(n.get('fat', 0) for n in nutr_per_ing), 1)
            sodium = round(sum(n.get('sod', 0) for n in nutr_per_ing), 1)
            sugar = round(sum(n.get('sug', 0) for n in nutr_per_ing), 1)
            saturates = 0
        else:
            calories = protein = fat = sodium = sugar = saturates = 0
    
    # Build search text
    title = recipe.get('title', '')
    search_parts = [title, title]  # Double weight title
    search_parts.extend(ingredients)
    search_parts.extend(recipe.get('categories', []))
    search_text = ' '.join(str(p).lower() for p in search_parts)
    
    return {
        'id': idx + 1,  # Use sequential ID
        'title': title,
        'description': recipe.get('desc', title),
        'ingredients': ingredients,
        'directions': directions,
        'categories': recipe.get('categories', []),
        'calories': calories,
        'protein': protein,
        'fat': fat,
        'sodium': sodium,
        'sugar': sugar,
        'saturates': saturates,
        'search_text': search_text
    }


def migrate():
    """Run the migration."""
    
    # Check DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("\nExample:")
        print("  export DATABASE_URL='postgresql://user:pass@host/dbname?sslmode=require'")
        sys.exit(1)
    
    print("=" * 60)
    print("Recipe Buddy - PostgreSQL Migration")
    print("=" * 60)
    
    # Find JSON file
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    json_gz_path = os.path.join(data_dir, 'halal_recipes.json.gz')
    json_path = os.path.join(data_dir, 'halal_recipes.json')
    
    if os.path.exists(json_gz_path):
        source_path = json_gz_path
        print(f"📁 Source: {json_gz_path}")
    elif os.path.exists(json_path):
        source_path = json_path
        print(f"📁 Source: {json_path}")
    else:
        print(f"❌ Recipe file not found in {data_dir}")
        sys.exit(1)
    
    # Create tables
    print("\n📊 Creating database tables...")
    engine = get_engine()
    Base.metadata.drop_all(engine)  # Drop existing tables
    Base.metadata.create_all(engine)
    print("✅ Tables created")
    
    # Load JSON
    print("\n📖 Loading recipes from JSON...")
    if source_path.endswith('.gz'):
        with gzip.open(source_path, 'rt', encoding='utf-8') as f:
            raw_recipes = json.load(f)
    else:
        with open(source_path, 'r', encoding='utf-8') as f:
            raw_recipes = json.load(f)
    
    print(f"📋 Found {len(raw_recipes):,} recipes")
    
    # Insert in batches
    print("\n💾 Inserting recipes into PostgreSQL...")
    session = get_session()
    
    batch_size = 500
    total = len(raw_recipes)
    inserted = 0
    
    try:
        for i in range(0, total, batch_size):
            batch = raw_recipes[i:i + batch_size]
            
            for j, raw_recipe in enumerate(batch):
                processed = preprocess_recipe(raw_recipe, i + j)
                recipe = Recipe(**processed)
                session.add(recipe)
            
            session.commit()
            inserted += len(batch)
            
            progress = (inserted / total) * 100
            print(f"  Progress: {inserted:,}/{total:,} ({progress:.1f}%)")
        
        print(f"\n✅ Inserted {inserted:,} recipes")
        
        # Enable trigram extension for similarity search
        print("\n🔍 Enabling pg_trgm extension...")
        try:
            session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            session.commit()
            print("✅ pg_trgm extension enabled")
        except Exception as e:
            print(f"⚠️ Could not enable pg_trgm (may need superuser): {e}")
            session.rollback()
        
        # Create indexes
        print("\n🔍 Creating search indexes...")
        session.execute(text("CREATE INDEX IF NOT EXISTS idx_recipe_title ON recipes (title)"))
        session.execute(text("CREATE INDEX IF NOT EXISTS idx_recipe_calories ON recipes (calories)"))
        session.execute(text("CREATE INDEX IF NOT EXISTS idx_recipe_protein ON recipes (protein)"))
        session.execute(text("CREATE INDEX IF NOT EXISTS idx_recipe_search_text ON recipes USING gin(to_tsvector('english', search_text))"))
        
        # Trigram index for similarity search
        try:
            session.execute(text("CREATE INDEX IF NOT EXISTS idx_recipe_title_trgm ON recipes USING gin(title gin_trgm_ops)"))
            session.execute(text("CREATE INDEX IF NOT EXISTS idx_recipe_search_trgm ON recipes USING gin(search_text gin_trgm_ops)"))
            print("✅ Trigram indexes created (similarity search enabled)")
        except Exception as e:
            print(f"⚠️ Could not create trigram indexes: {e}")
        
        session.commit()
        print("✅ Indexes created")
        
        # Verify
        count = session.query(Recipe).count()
        print(f"\n✅ Migration complete! {count:,} recipes in database")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    migrate()
