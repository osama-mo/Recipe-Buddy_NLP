"""
Additional Features API Routes
- Similar Recipes
- Meal Planning
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any

from core.similarity_engine import SimilarityEngine
from core.meal_planner import MealPlanAssistant


features_bp = Blueprint('features', __name__, url_prefix='/api')

# Initialize engines (will be done in route init)
similarity_engine = None
meal_planner = None


def init_features_routes():
    """Initialize the features routes."""
    global similarity_engine, meal_planner
    
    similarity_engine = SimilarityEngine()
    meal_planner = MealPlanAssistant()
    
    print("✅ Features routes initialized (similar recipes, meal planning)")


@features_bp.route('/recipes/<int:recipe_id>/similar', methods=['GET'])
def get_similar_recipes(recipe_id: int):
    """
    Get recipes similar to a specific recipe.
    
    Query Parameters:
        limit (int): Maximum number of similar recipes (default: 10, max: 20)
        min_score (float): Minimum similarity score 0-1 (default: 0.3)
    
    Example:
        GET /api/recipes/123/similar?limit=5&min_score=0.4
    
    Returns:
        {
            "recipe_id": 123,
            "similar_recipes": [
                {
                    "id": 456,
                    "title": "Similar Recipe",
                    "similarity_score": 0.85,
                    "similarity_reasons": ["Shares ingredients: chicken, tomato", ...],
                    "nutrition": {...}
                }
            ],
            "count": 5
        }
    """
    try:
        # Get parameters
        limit = min(int(request.args.get('limit', 10)), 20)
        min_score = float(request.args.get('min_score', 0.3))
        
        # Validate
        if min_score < 0 or min_score > 1:
            return jsonify({
                'error': 'min_score must be between 0 and 1'
            }), 400
        
        # Find similar recipes
        similar = similarity_engine.find_similar(
            recipe_id=recipe_id,
            limit=limit,
            min_score=min_score
        )
        
        if not similar:
            return jsonify({
                'recipe_id': recipe_id,
                'similar_recipes': [],
                'count': 0,
                'message': 'No similar recipes found. Try lowering min_score.'
            }), 200
        
        return jsonify({
            'recipe_id': recipe_id,
            'similar_recipes': similar,
            'count': len(similar)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'error': f'Failed to find similar recipes: {str(e)}'
        }), 500


@features_bp.route('/meal-plan', methods=['POST'])
def generate_meal_plan():
    """
    Generate a meal plan based on preferences and nutrition goals.
    
    Request Body:
        {
            "days": 7,                          // Number of days (1-7)
            "meals_per_day": 3,                 // Meals per day (2-4)
            "preferences": {                    // Optional
                "vegetarian": true,
                "high_protein": true,
                "no_dairy": false,
                "no_gluten": false,
                "no_nuts": false,
                "low_carb": false
            },
            "nutrition_goals": {                // Optional, daily targets
                "calories": 2000,
                "protein": 150,
                "fat": 65,
                "sodium": 2300
            },
            "variety_weight": 0.7               // 0-1, higher = more variety
        }
    
    Example:
        POST /api/meal-plan
        {
            "days": 3,
            "meals_per_day": 3,
            "preferences": {"high_protein": true},
            "nutrition_goals": {"calories": 2200, "protein": 150}
        }
    
    Returns:
        {
            "meal_plan": [
                {
                    "day": 1,
                    "date": "2025-12-10",
                    "meals": [
                        {
                            "title": "Protein Pancakes",
                            "meal_type": "breakfast",
                            "meal_number": 1,
                            "nutrition": {...}
                        },
                        ...
                    ],
                    "daily_totals": {"calories": 2150, "protein": 145}
                }
            ],
            "summary": {
                "total_nutrition": {...},
                "daily_average": {...},
                "goal_achievement": {...},
                "total_recipes": 21
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        # Extract parameters with defaults
        days = data.get('days', 7)
        meals_per_day = data.get('meals_per_day', 3)
        preferences = data.get('preferences', {})
        nutrition_goals = data.get('nutrition_goals')
        variety_weight = data.get('variety_weight', 0.7)
        
        # Validate
        if not isinstance(days, int) or days < 1 or days > 7:
            return jsonify({
                'error': 'days must be an integer between 1 and 7'
            }), 400
        
        if not isinstance(meals_per_day, int) or meals_per_day < 2 or meals_per_day > 4:
            return jsonify({
                'error': 'meals_per_day must be an integer between 2 and 4'
            }), 400
        
        if not isinstance(variety_weight, (int, float)) or variety_weight < 0 or variety_weight > 1:
            return jsonify({
                'error': 'variety_weight must be a number between 0 and 1'
            }), 400
        
        # Generate meal plan
        meal_plan_result = meal_planner.generate_meal_plan(
            days=days,
            preferences=preferences,
            nutrition_goals=nutrition_goals,
            meals_per_day=meals_per_day,
            variety_weight=variety_weight
        )
        
        return jsonify(meal_plan_result), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to generate meal plan: {str(e)}'
        }), 500


@features_bp.route('/meal-plan/quick', methods=['GET'])
def quick_meal_plan():
    """
    Generate a quick 3-day meal plan with common preferences.
    
    Query Parameters:
        diet (str): vegetarian, high_protein, low_carb, balanced (default)
        calories (int): Daily calorie target (default: 2000)
    
    Example:
        GET /api/meal-plan/quick?diet=high_protein&calories=2200
    
    Returns:
        Same as POST /api/meal-plan but with preset configurations
    """
    try:
        # Get parameters
        diet_type = request.args.get('diet', 'balanced').lower()
        calories = int(request.args.get('calories', 2000))
        
        # Build preferences based on diet type
        preferences = {}
        nutrition_goals = {'calories': calories}
        
        if diet_type == 'vegetarian':
            preferences['vegetarian'] = True
            nutrition_goals['protein'] = 60
        elif diet_type == 'high_protein':
            preferences['high_protein'] = True
            nutrition_goals['protein'] = 150
        elif diet_type == 'low_carb':
            preferences['low_carb'] = True
            nutrition_goals['protein'] = 100
        else:  # balanced
            nutrition_goals['protein'] = 75
        
        # Generate 3-day plan
        meal_plan_result = meal_planner.generate_meal_plan(
            days=3,
            preferences=preferences,
            nutrition_goals=nutrition_goals,
            meals_per_day=3,
            variety_weight=0.7
        )
        
        return jsonify(meal_plan_result), 200
        
    except ValueError as e:
        return jsonify({
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'error': f'Failed to generate quick meal plan: {str(e)}'
        }), 500
