"""
Recipe API Routes
Handles individual recipe and listing endpoints
"""

import random
from flask import Blueprint, request, jsonify

# Will be injected by app
recipes = None
recipe_matcher = None

recipe_bp = Blueprint('recipes', __name__)


def init_recipe_routes(recipes_list, matcher):
    """Initialize with recipes and matcher instances."""
    global recipes, recipe_matcher
    recipes = recipes_list
    recipe_matcher = matcher


@recipe_bp.route('/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get a specific recipe by its ID."""
    from config.settings import USE_DATABASE
    
    if USE_DATABASE:
        # Database mode: query by actual ID
        from core.models import get_session, Recipe
        session = get_session()
        try:
            recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()
            if not recipe:
                return jsonify({'error': 'Recipe not found'}), 404
            
            return jsonify({
                'id': recipe.id,
                'recipe': {
                    'title': recipe.title,
                    'description': recipe.description or recipe.title,
                    'categories': recipe.categories or [],
                    'ingredients': recipe.ingredients or [],
                    'directions': recipe.directions or [],
                    'nutrition': {
                        'calories': recipe.calories or 0,
                        'protein': recipe.protein or 0,
                        'fat': recipe.fat or 0,
                        'sodium': recipe.sodium or 0,
                        'sugar': recipe.sugar or 0,
                        'saturates': recipe.saturates or 0
                    }
                }
            })
        finally:
            session.close()
    else:
        # JSON mode: find by id field in recipe dict
        for recipe in recipes:
            if recipe.get('id') == recipe_id:
                return jsonify({
                    'id': recipe_id,
                    'recipe': {
                        'title': recipe.get('title', 'Untitled'),
                        'description': recipe.get('desc', recipe.get('title', '')),
                        'categories': recipe.get('categories', []),
                        'ingredients': recipe.get('ingredients', []),
                        'directions': recipe.get('directions', []),
                        'nutrition': {
                            'calories': recipe.get('calories', 0),
                            'protein': recipe.get('protein', 0),
                            'fat': recipe.get('fat', 0),
                            'sodium': recipe.get('sodium', 0),
                            'sugar': recipe.get('sugar', 0),
                            'saturates': recipe.get('saturates', 0)
                        },
                        'rating': recipe.get('rating'),
                        'url': recipe.get('url')
                    }
                })
        
        return jsonify({'error': 'Recipe not found'}), 404


@recipe_bp.route('/random', methods=['GET'])
def random_recipes():
    """Get random recipes."""
    from config.settings import USE_DATABASE
    
    count = int(request.args.get('count', 5))
    count = min(count, 50)  # Limit to 50
    
    if USE_DATABASE:
        # Database mode: use SQL random
        from core.models import get_session, Recipe
        from sqlalchemy.sql.expression import func
        
        session = get_session()
        try:
            random_recipes = session.query(Recipe).order_by(func.random()).limit(count).all()
            
            results = []
            for recipe in random_recipes:
                results.append({
                    'id': recipe.id,
                    'title': recipe.title,
                    'categories': recipe.categories or [],
                    'calories': recipe.calories,
                    'protein': recipe.protein
                })
            
            return jsonify({
                'count': len(results),
                'recipes': results
            })
        finally:
            session.close()
    else:
        # JSON mode
        indices = random.sample(range(len(recipes)), min(count, len(recipes)))
        
        results = []
        for idx in indices:
            recipe = recipes[idx]
            results.append({
                'id': recipe.get('id', idx),  # Use recipe's id if available
                'title': recipe.get('title', 'Untitled'),
                'categories': recipe.get('categories', []),
                'calories': recipe.get('calories'),
                'protein': recipe.get('protein')
            })
        
        return jsonify({
            'count': len(results),
            'recipes': results
        })


@recipe_bp.route('/categories', methods=['GET'])
def list_categories():
    """List all available categories."""
    from config.settings import USE_DATABASE
    
    if USE_DATABASE:
        # Database mode: query categories directly
        from core.models import get_session, Recipe
        from sqlalchemy import func
        
        session = get_session()
        try:
            # Use unnest to expand arrays and count
            from sqlalchemy import text
            result = session.execute(text("""
                SELECT category, COUNT(*) as count
                FROM recipes, unnest(categories) AS category
                GROUP BY category
                ORDER BY count DESC
            """))
            
            categories = [{'name': row[0], 'count': row[1]} for row in result]
            
            return jsonify({
                'total_categories': len(categories),
                'categories': categories
            })
        finally:
            session.close()
    else:
        # JSON mode
        categories = {}
        for recipe in recipes:
            for cat in recipe.get('categories', []):
                categories[cat] = categories.get(cat, 0) + 1
        
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        return jsonify({
            'total_categories': len(sorted_categories),
            'categories': [{'name': cat, 'count': count} for cat, count in sorted_categories]
        })


@recipe_bp.route('/ingredients', methods=['GET'])
def list_ingredients():
    """List common ingredients recognized by the system."""
    from config.vocabulary import COMMON_INGREDIENTS
    
    return jsonify({
        'total_ingredients': len(COMMON_INGREDIENTS),
        'ingredients': COMMON_INGREDIENTS[:100]
    })
