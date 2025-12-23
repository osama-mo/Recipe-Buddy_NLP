"""
Meal Plan Assistant
Generates balanced meal plans based on user preferences and nutrition goals
"""

import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from core.models import get_session, Recipe
from core.recipe_matcher import RecipeMatcher
from core.query_parser import QueryParser


class MealPlanAssistant:
    """
    Generate meal plans with balanced nutrition and variety.
    
    Features:
    - Multi-day meal plans (3-7 days)
    - Nutrition goal tracking (daily targets)
    - Ingredient variety (avoid repeating same ingredients)
    - Meal type distribution (breakfast, lunch, dinner, snack)
    """
    
    def __init__(self):
        """Initialize meal plan assistant."""
        self.session = None
        self.query_parser = QueryParser()
        
    def generate_meal_plan(self, 
                          days: int = 7,
                          preferences: Optional[Dict[str, Any]] = None,
                          nutrition_goals: Optional[Dict[str, Any]] = None,
                          meals_per_day: int = 3,
                          variety_weight: float = 0.7) -> Dict[str, Any]:
        """
        Generate a meal plan.
        
        Args:
            days: Number of days (1-7)
            preferences: User preferences (e.g., {'vegetarian': True, 'no_dairy': True})
            nutrition_goals: Daily nutrition targets (e.g., {'calories': 2000, 'protein': 150})
            meals_per_day: Number of meals per day (2-4)
            variety_weight: How much to prioritize variety (0-1, higher = more variety)
            
        Returns:
            Meal plan with recipes and nutrition summary
        """
        days = max(1, min(days, 7))  # Clamp to 1-7 days
        meals_per_day = max(2, min(meals_per_day, 4))  # Clamp to 2-4 meals
        
        preferences = preferences or {}
        nutrition_goals = nutrition_goals or self._default_nutrition_goals()
        
        self.session = get_session()
        
        try:
            # Generate meal plan
            meal_plan = self._generate_plan(
                days, preferences, nutrition_goals, 
                meals_per_day, variety_weight
            )
            
            # Calculate nutrition summary
            summary = self._calculate_nutrition_summary(meal_plan, nutrition_goals)
            
            return {
                'meal_plan': meal_plan,
                'summary': summary,
                'preferences': preferences,
                'nutrition_goals': nutrition_goals,
                'generated_at': datetime.now().isoformat()
            }
            
        finally:
            if self.session:
                self.session.close()
    
    def _generate_plan(self, days: int, preferences: Dict[str, Any],
                      nutrition_goals: Dict[str, Any], meals_per_day: int,
                      variety_weight: float) -> List[Dict[str, Any]]:
        """Generate the actual meal plan."""
        from sqlalchemy import func, or_
        
        meal_plan = []
        used_recipe_ids = set()
        used_ingredients = defaultdict(int)  # Track ingredient usage
        
        # Meal type distribution
        meal_types = self._get_meal_type_distribution(meals_per_day)
        
        # Calculate target calories per meal
        daily_calories = nutrition_goals.get('calories', 2000)
        calories_per_meal = daily_calories / meals_per_day
        
        for day_num in range(1, days + 1):
            day_meals = []
            day_calories = 0
            day_protein = 0
            
            for meal_idx, meal_type in enumerate(meal_types):
                # Build query constraints for this meal
                constraints = self._build_meal_constraints(
                    meal_type, preferences, nutrition_goals,
                    calories_per_meal, day_calories, daily_calories
                )
                
                # Get candidate recipes
                candidates = self._get_meal_candidates(
                    constraints, used_recipe_ids, limit=50
                )
                
                if not candidates:
                    # Fallback: relax constraints
                    candidates = self._get_meal_candidates(
                        {'meal_type': meal_type}, used_recipe_ids, limit=20
                    )
                
                if candidates:
                    # Select recipe based on variety
                    selected = self._select_recipe_with_variety(
                        candidates, used_ingredients, variety_weight
                    )
                    
                    # Add to plan
                    meal_dict = selected.to_slim_dict()
                    meal_dict['meal_type'] = meal_type
                    meal_dict['meal_number'] = meal_idx + 1
                    meal_dict['nutrition'] = {
                        'calories': selected.calories or 0,
                        'protein': selected.protein or 0,
                        'fat': selected.fat or 0,
                        'sodium': selected.sodium or 0,
                        'sugar': selected.sugar or 0,
                        'saturates': selected.saturates or 0
                    }
                    
                    day_meals.append(meal_dict)
                    
                    # Update tracking
                    used_recipe_ids.add(selected.id)
                    day_calories += (selected.calories or 0)
                    day_protein += (selected.protein or 0)
                    
                    # Track ingredients
                    if selected.ingredients:
                        for ing in selected.ingredients[:5]:  # Track top ingredients
                            # Extract main ingredient word
                            words = ing.lower().split()
                            main_word = next((w for w in words if len(w) > 4), words[0] if words else '')
                            if main_word:
                                used_ingredients[main_word] += 1
            
            # Add day to plan
            meal_plan.append({
                'day': day_num,
                'date': (datetime.now() + timedelta(days=day_num-1)).strftime('%Y-%m-%d'),
                'meals': day_meals,
                'daily_totals': {
                    'calories': round(day_calories, 1),
                    'protein': round(day_protein, 1)
                }
            })
        
        return meal_plan
    
    def _get_meal_type_distribution(self, meals_per_day: int) -> List[str]:
        """Get meal type distribution based on meals per day."""
        if meals_per_day == 2:
            return ['breakfast', 'dinner']
        elif meals_per_day == 3:
            return ['breakfast', 'lunch', 'dinner']
        elif meals_per_day == 4:
            return ['breakfast', 'snack', 'lunch', 'dinner']
        else:
            return ['breakfast', 'lunch', 'dinner']
    
    def _build_meal_constraints(self, meal_type: str, preferences: Dict[str, Any],
                                nutrition_goals: Dict[str, Any], calories_per_meal: float,
                                day_calories: float, daily_calories: float) -> Dict[str, Any]:
        """Build SQL constraints for meal selection."""
        constraints = {'meal_type': meal_type}
        
        # Calorie constraints (±30% of target per meal)
        remaining_calories = daily_calories - day_calories
        if remaining_calories > 0:
            min_cal = max(50, calories_per_meal * 0.7)
            max_cal = min(remaining_calories, calories_per_meal * 1.3)
            constraints['calories'] = {'min': min_cal, 'max': max_cal}
        
        # Protein goals (if high protein diet)
        if nutrition_goals.get('protein', 0) >= 100:  # High protein
            if meal_type in ['breakfast', 'lunch', 'dinner']:
                constraints['protein_min'] = 15  # At least 15g per main meal
        
        # User preferences
        if preferences.get('vegetarian'):
            constraints['vegetarian'] = True
        
        if preferences.get('low_carb'):
            constraints['carb_max'] = 30  # Low carb meals
        
        if preferences.get('high_protein'):
            constraints['protein_min'] = 20
        
        # Excluded ingredients
        excluded = []
        if preferences.get('no_dairy'):
            excluded.extend(['milk', 'cheese', 'butter', 'cream', 'yogurt'])
        if preferences.get('no_gluten'):
            excluded.extend(['flour', 'wheat', 'bread', 'pasta'])
        if preferences.get('no_nuts'):
            excluded.extend(['peanut', 'almond', 'walnut', 'cashew'])
        
        if excluded:
            constraints['excluded_ingredients'] = excluded
        
        return constraints
    
    def _get_meal_candidates(self, constraints: Dict[str, Any], 
                            used_recipe_ids: set, limit: int = 50) -> List[Recipe]:
        """Get candidate recipes matching constraints."""
        from sqlalchemy import or_, and_, func
        
        query = self.session.query(Recipe)
        
        # Filter out already used recipes
        if used_recipe_ids:
            query = query.filter(~Recipe.id.in_(used_recipe_ids))
        
        # Meal type filter
        meal_type = constraints.get('meal_type')
        if meal_type:
            query = query.filter(
                func.lower(Recipe.search_text).like(f'%{meal_type}%')
            )
        
        # Calorie constraints
        if 'calories' in constraints:
            cal_constraints = constraints['calories']
            if 'min' in cal_constraints:
                query = query.filter(Recipe.calories >= cal_constraints['min'])
            if 'max' in cal_constraints:
                query = query.filter(Recipe.calories <= cal_constraints['max'])
        
        # Protein constraints
        if 'protein_min' in constraints:
            query = query.filter(Recipe.protein >= constraints['protein_min'])
        
        # Vegetarian filter
        if constraints.get('vegetarian'):
            query = query.filter(
                func.lower(Recipe.search_text).like('%vegetarian%')
            )
        
        # Excluded ingredients
        excluded = constraints.get('excluded_ingredients', [])
        for exc in excluded:
            pattern = f'%{exc.lower()}%'
            query = query.filter(~func.lower(Recipe.search_text).like(pattern))
        
        # Ensure nutrition data exists
        query = query.filter(
            Recipe.calories.isnot(None),
            Recipe.calories > 0
        )
        
        # Get random candidates for variety
        candidates = query.order_by(func.random()).limit(limit).all()
        
        return candidates
    
    def _select_recipe_with_variety(self, candidates: List[Recipe],
                                   used_ingredients: Dict[str, int],
                                   variety_weight: float) -> Recipe:
        """
        Select recipe that maximizes variety.
        
        Variety score based on:
        - How many new ingredients it introduces
        - How few repeated ingredients it has
        """
        if not candidates:
            return None
        
        if variety_weight < 0.1:
            # Low variety weight: just pick random
            return random.choice(candidates)
        
        best_recipe = None
        best_score = -1
        
        for recipe in candidates:
            variety_score = 0
            
            if recipe.ingredients:
                # Count new vs repeated ingredients
                new_ingredients = 0
                repeated_ingredients = 0
                
                for ing in recipe.ingredients[:5]:
                    words = ing.lower().split()
                    main_word = next((w for w in words if len(w) > 4), words[0] if words else '')
                    
                    if main_word:
                        if used_ingredients.get(main_word, 0) == 0:
                            new_ingredients += 1
                        else:
                            repeated_ingredients += 1
                
                # Variety score: favor new ingredients
                variety_score = new_ingredients - (repeated_ingredients * 0.5)
            
            # Combine with random factor (to avoid being too deterministic)
            random_factor = random.random() * (1 - variety_weight)
            total_score = variety_score * variety_weight + random_factor
            
            if total_score > best_score:
                best_score = total_score
                best_recipe = recipe
        
        return best_recipe or candidates[0]
    
    def _calculate_nutrition_summary(self, meal_plan: List[Dict[str, Any]],
                                    nutrition_goals: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate nutrition summary for the meal plan."""
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'sodium': 0,
            'sugar': 0
        }
        
        for day in meal_plan:
            for meal in day['meals']:
                nutrition = meal.get('nutrition', {})
                total_nutrition['calories'] += nutrition.get('calories', 0)
                total_nutrition['protein'] += nutrition.get('protein', 0)
                total_nutrition['fat'] += nutrition.get('fat', 0)
                total_nutrition['sodium'] += nutrition.get('sodium', 0)
                total_nutrition['sugar'] += nutrition.get('sugar', 0)
        
        # Calculate averages
        num_days = len(meal_plan)
        avg_nutrition = {
            'calories': round(total_nutrition['calories'] / num_days, 1),
            'protein': round(total_nutrition['protein'] / num_days, 1),
            'fat': round(total_nutrition['fat'] / num_days, 1),
            'sodium': round(total_nutrition['sodium'] / num_days, 1),
            'sugar': round(total_nutrition['sugar'] / num_days, 1)
        }
        
        # Calculate goal achievement
        goal_achievement = {}
        for nutrient, goal_value in nutrition_goals.items():
            actual_value = avg_nutrition.get(nutrient, 0)
            if goal_value > 0:
                achievement_pct = (actual_value / goal_value) * 100
                goal_achievement[nutrient] = {
                    'target': goal_value,
                    'actual': actual_value,
                    'achievement': round(achievement_pct, 1)
                }
        
        return {
            'total_nutrition': total_nutrition,
            'daily_average': avg_nutrition,
            'goal_achievement': goal_achievement,
            'total_recipes': sum(len(day['meals']) for day in meal_plan)
        }
    
    def _default_nutrition_goals(self) -> Dict[str, float]:
        """Default nutrition goals (moderate, balanced diet)."""
        return {
            'calories': 2000,
            'protein': 75,
            'fat': 65,
            'sodium': 2300
        }


if __name__ == "__main__":
    # Test the meal plan assistant
    # Ensure DATABASE_URL is set in your environment before running
    import os
    import json
    
    if not os.environ.get('DATABASE_URL'):
        print("ERROR: Set DATABASE_URL environment variable first")
        exit(1)
    
    assistant = MealPlanAssistant()
    
    # Generate a 3-day high-protein meal plan
    plan = assistant.generate_meal_plan(
        days=3,
        preferences={'high_protein': True, 'no_dairy': False},
        nutrition_goals={'calories': 2200, 'protein': 150},
        meals_per_day=3
    )
    
    print(json.dumps(plan, indent=2))
