"""
Recipe Matcher Module
Hybrid search using TF-IDF + rule-based scoring
Supports both in-memory (JSON) and database (PostgreSQL) modes
"""

import numpy as np
from typing import Dict, List, Any, Optional

from config.settings import (
    TFIDF_MAX_FEATURES, TFIDF_NGRAM_RANGE,
    TFIDF_MIN_DF, TFIDF_MAX_DF,
    RULE_BASED_WEIGHT, TFIDF_WEIGHT,
    USE_DATABASE
)


class RecipeMatcher:
    """
    Hybrid recipe matcher combining rule-based and ML approaches.
    
    V2.1: Supports PostgreSQL database mode for efficient querying.
    """
    
    def __init__(self, recipes: List[Dict[str, Any]], metadata: Dict[str, Any] = None):
        """Initialize with recipe dataset."""
        self.recipes = recipes
        self.metadata = metadata or {}
        self.use_database = USE_DATABASE
        self.tfidf_vectorizer = None
        self.recipe_vectors = None
        
        # Only build TF-IDF if not using database
        if not self.use_database and recipes:
            self._build_tfidf_index()
        elif self.use_database:
            print("✅ Using PostgreSQL database mode (no TF-IDF needed)")
    
    def _build_tfidf_index(self):
        """Build TF-IDF index for semantic search (only for JSON mode)."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        import gc
        
        print("Building TF-IDF index...")
        
        recipe_texts = [self._recipe_to_text(r) for r in self.recipes]
        gc.collect()
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=TFIDF_NGRAM_RANGE,
            stop_words='english',
            min_df=TFIDF_MIN_DF,
            max_df=TFIDF_MAX_DF,
            dtype='float32'
        )
        
        self.recipe_vectors = self.tfidf_vectorizer.fit_transform(recipe_texts)
        del recipe_texts
        gc.collect()
        print(f"TF-IDF index built with {self.recipe_vectors.shape[1]} features")
    
    def _recipe_to_text(self, recipe: Dict[str, Any]) -> str:
        """Convert recipe to searchable text (compact version)."""
        parts = []
        
        title = recipe.get('title', '')
        parts.append(title)  # Single weight for title (saves memory)
        
        # Skip desc to save memory - title is usually enough
        
        if recipe.get('ingredients'):
            if isinstance(recipe['ingredients'], list):
                parts.append(' '.join(str(ing) for ing in recipe['ingredients']))
            else:
                parts.append(str(recipe['ingredients']))
        
        if recipe.get('directions'):
            if isinstance(recipe['directions'], list):
                parts.append(' '.join(str(d) for d in recipe['directions']))
        
        if recipe.get('categories'):
            if isinstance(recipe['categories'], list):
                parts.append(' '.join(str(c) for c in recipe['categories']))
        
        return ' '.join(parts).lower()
    
    def search(self, parsed_query: Dict[str, Any], max_results: int = 10, 
               use_tfidf: bool = True, query: str = None,
               page: int = 1, offset: int = None) -> List[Dict[str, Any]]:
        """
        Search recipes using hybrid approach with pagination support.
        
        Args:
            parsed_query: Parsed query from QueryParser
            max_results: Maximum results to return
            use_tfidf: Whether to use TF-IDF scoring
            query: Optional raw query string
            page: Page number (1-indexed)
            offset: Direct offset (overrides page if provided)
        """
        # Calculate offset
        if offset is None:
            offset = 0  # For backward compatibility, get all up to max_results
        
        # Use database search if available
        if self.use_database:
            return self._search_database(parsed_query, max_results, offset)
        
        # Otherwise use in-memory search with TF-IDF
        return self._search_memory(parsed_query, max_results, use_tfidf, query)
    
    def _search_database(self, parsed_query: Dict[str, Any], max_results: int, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search using PostgreSQL database with v2_enhanced scoring logic.
        
        Follows v2_enhanced approach:
        1. First check exclusions (instant reject)
        2. Then check nutrition requirements (instant reject)
        3. Then check required ingredients (instant reject if missing)
        4. Only then calculate scores for valid matches
        """
        from core.models import get_session, Recipe
        from sqlalchemy import or_, and_, func, desc, literal
        
        session = get_session()
        try:
            # Start building query - get more candidates for post-processing
            query = session.query(Recipe)
            
            # Build search terms
            search_terms = []
            required_ingredients = parsed_query.get('ingredients', [])
            dish_name = parsed_query.get('dish_name')
            categories = parsed_query.get('categories', [])
            
            if dish_name:
                search_terms.append(dish_name)
            if required_ingredients:
                search_terms.extend(required_ingredients)
            if categories:
                search_terms.extend(categories)
            
            # STEP 1: EXCLUDE RECIPES WITH EXCLUDED INGREDIENTS (instant reject)
            excluded = parsed_query.get('excluded_ingredients', [])
            for exc in excluded:
                # Check for individual words (e.g., "oil" not just "olive oil")
                exc_lower = exc.lower()
                # Use word boundaries to match whole words
                exc_pattern = f"%{exc_lower}%"
                query = query.filter(
                    ~and_(
                        func.lower(Recipe.search_text).like(exc_pattern),
                        or_(
                            func.lower(Recipe.title).like(exc_pattern),
                            func.lower(Recipe.search_text).like(exc_pattern)
                        )
                    )
                )
            
            # STEP 2: APPLY NUTRITION FILTERS (instant reject if not met)
            nutrition_req = parsed_query.get('nutrition', {})
            for nutrient, constraints in nutrition_req.items():
                column = getattr(Recipe, nutrient, None)
                if column is not None:
                    # Recipe must have nutrition data
                    query = query.filter(column.isnot(None))
                    
                    if 'min' in constraints:
                        query = query.filter(column >= constraints['min'])
                    if 'max' in constraints:
                        query = query.filter(column <= constraints['max'])
            
            # STEP 3: FILTER BY REQUIRED INGREDIENTS (must have ALL)
            # Each required ingredient must appear in search_text or title
            if required_ingredients:
                for ingredient in required_ingredients:
                    ing_pattern = f"%{ingredient.lower()}%"
                    query = query.filter(
                        or_(
                            func.lower(Recipe.title).like(ing_pattern),
                            func.lower(Recipe.search_text).like(ing_pattern)
                        )
                    )
            
            # STEP 4: FILTER BY DISH NAME (if specified)
            if dish_name:
                dish_pattern = f"%{dish_name.lower()}%"
                query = query.filter(
                    or_(
                        func.lower(Recipe.title).like(dish_pattern),
                        func.lower(Recipe.search_text).like(dish_pattern)
                    )
                )
            
            # Get more candidates than needed (for scoring)
            candidates = query.limit(max_results * 10).all()
            
            # STEP 5: CALCULATE RULE-BASED SCORES (v2_enhanced style)
            scored_recipes = []
            for recipe in candidates:
                score = self._calculate_recipe_score(recipe, parsed_query)
                
                if score > 0:  # Only include recipes with positive scores
                    recipe_dict = recipe.to_slim_dict()
                    recipe_dict['score'] = round(score / 100.0, 3)  # Normalize to 0-1
                    recipe_dict['rule_score'] = round(score / 100.0, 3)
                    recipe_dict['semantic_score'] = round(score / 100.0, 3)
                    recipe_dict['match_reasons'] = self._get_match_reasons(recipe_dict, parsed_query)
                    recipe_dict['nutrition'] = {
                        'calories': recipe.calories or 0,
                        'protein': recipe.protein or 0,
                        'fat': recipe.fat or 0,
                        'sodium': recipe.sodium or 0,
                        'sugar': recipe.sugar or 0,
                        'saturates': recipe.saturates or 0
                    }
                    scored_recipes.append(recipe_dict)
            
            # STEP 6: SORT BY SCORE AND PAGINATE
            scored_recipes.sort(key=lambda x: x['score'], reverse=True)
            
            # Apply offset and limit for pagination
            start_idx = offset
            end_idx = offset + max_results
            return scored_recipes[start_idx:end_idx]
            
        finally:
            session.close()
    
    def _calculate_recipe_score(self, recipe, parsed_query: Dict[str, Any]) -> float:
        """
        Calculate v2_enhanced style rule-based score (0-100).
        
        Scoring breakdown:
        - Dish name match: up to 100 points
        - Required ingredient in title: up to 25 points each
        - Required ingredient in recipe: 10 points each
        - Category match: 12-15 points each
        - Nutrition match: 20 points per constraint
        - Combo bonus: up to 30 points
        """
        score = 0.0
        title_lower = (recipe.title or '').lower()
        search_text_lower = (recipe.search_text or '').lower()
        
        # DISH NAME SCORING (v2_enhanced logic)
        dish_name = parsed_query.get('dish_name')
        if dish_name:
            dish_lower = dish_name.lower()
            
            # Exact title match
            if title_lower == dish_lower:
                score += 100
            # Whole word in title
            elif f" {dish_lower} " in f" {title_lower} ":
                title_words = title_lower.split()
                if dish_lower in title_words:
                    position = title_words.index(dish_lower)
                    if position == 0:
                        score += 60  # First word
                    elif position == len(title_words) - 1:
                        score += 65  # Last word
                    else:
                        score += 55  # Middle
                else:
                    score += 50
            # Partial match in title
            elif dish_lower in title_lower:
                score += 35
            # In categories/text
            elif dish_lower in search_text_lower:
                score += 20
        
        # REQUIRED INGREDIENTS SCORING
        required_ingredients = parsed_query.get('ingredients', [])
        for ingredient in required_ingredients:
            ing_lower = ingredient.lower()
            
            # Ingredient in title (higher value)
            if ing_lower in title_lower:
                title_words = title_lower.split()
                ing_score = 15
                
                # Position bonus
                if ing_lower in title_words:
                    position = title_words.index(ing_lower)
                    if position == 0:
                        ing_score += 10  # First word
                    elif position == 1:
                        ing_score += 8
                    elif position == 2:
                        ing_score += 5
                    else:
                        ing_score += 2
                else:
                    ing_score += 5
                
                score += ing_score
            
            # Ingredient in recipe text
            if ing_lower in search_text_lower:
                score += 10
        
        # COMBO BONUS (dish + ingredients together in title)
        if dish_name and required_ingredients:
            dish_lower = dish_name.lower()
            ingredients_in_title = sum(1 for ing in required_ingredients if ing.lower() in title_lower)
            
            if dish_lower in title_lower and ingredients_in_title > 0:
                score += 20
                # Proximity bonus
                title_words = title_lower.split()
                if dish_lower in title_words:
                    for ing in required_ingredients:
                        ing_lower = ing.lower()
                        if ing_lower in title_words:
                            try:
                                dish_idx = title_words.index(dish_lower)
                                ing_idx = title_words.index(ing_lower)
                                distance = abs(dish_idx - ing_idx)
                                if distance <= 2:
                                    score += 10  # Close together
                            except ValueError:
                                pass
        
        # CATEGORY SCORING
        categories = parsed_query.get('categories', [])
        for category in categories:
            cat_lower = category.lower()
            if cat_lower in search_text_lower:
                score += 12
        
        # MEAL TYPE SCORING
        meal_type = parsed_query.get('meal_type')
        if meal_type and meal_type.lower() in search_text_lower:
            score += 15
        
        # NUTRITION SCORING (bonus for meeting requirements)
        nutrition_req = parsed_query.get('nutrition', {})
        if nutrition_req:
            score += 20 * len(nutrition_req)  # Bonus for each nutrition constraint met
        
        return score
    
    def _search_memory(self, parsed_query: Dict[str, Any], max_results: int,
                       use_tfidf: bool, query: str) -> List[Dict[str, Any]]:
        """Search using in-memory TF-IDF (for JSON mode)."""
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Build query string from parsed_query if not provided
        if query is None:
            query_parts = []
            if parsed_query.get('dish_name'):
                query_parts.append(parsed_query['dish_name'])
            if parsed_query.get('ingredients'):
                query_parts.extend(parsed_query['ingredients'])
            if parsed_query.get('categories'):
                query_parts.extend(parsed_query['categories'])
            query = ' '.join(query_parts) if query_parts else 'recipe'
        
        # Calculate scores
        if use_tfidf and self.tfidf_vectorizer:
            query_vector = self.tfidf_vectorizer.transform([query.lower()])
            semantic_scores = cosine_similarity(query_vector, self.recipe_vectors).flatten()
        else:
            semantic_scores = np.zeros(len(self.recipes))
        
        rule_scores = self._calculate_rule_scores(parsed_query)
        
        # Hybrid scoring
        if use_tfidf and self.tfidf_vectorizer:
            hybrid_scores = RULE_BASED_WEIGHT * rule_scores + TFIDF_WEIGHT * semantic_scores
        else:
            hybrid_scores = rule_scores
        
        # Apply constraints
        constraint_mask = self._apply_constraints(parsed_query)
        hybrid_scores = hybrid_scores * constraint_mask
        
        # Get top results
        top_indices = np.argsort(hybrid_scores)[::-1][:max_results * 3]
        
        results = []
        for idx in top_indices:
            if hybrid_scores[idx] <= 0:
                continue
            
            recipe = self.recipes[idx]
            result = {
                'id': int(idx),
                'title': recipe.get('title', 'Unknown'),
                'description': recipe.get('desc', recipe.get('title', '')),
                'categories': recipe.get('categories', []),
                'ingredients': recipe.get('ingredients', [])[:10],
                'directions': recipe.get('directions', [])[:3],  # First 3 steps preview
                'score': round(float(hybrid_scores[idx]), 3),
                'semantic_score': round(float(semantic_scores[idx]), 3) if use_tfidf else 0,
                'rule_score': round(float(rule_scores[idx]), 3),
                'match_reasons': self._get_match_reasons(recipe, parsed_query),
                'nutrition': {
                    'calories': self._safe_number(recipe.get('calories', 0)),
                    'protein': self._safe_number(recipe.get('protein', 0)),
                    'fat': self._safe_number(recipe.get('fat', 0)),
                    'sodium': self._safe_number(recipe.get('sodium', 0)),
                    'sugar': self._safe_number(recipe.get('sugar', 0)),
                    'saturates': self._safe_number(recipe.get('saturates', 0))
                }
            }
            results.append(result)
            
            if len(results) >= max_results:
                break
        
        return results
    
    def _calculate_rule_scores(self, parsed_query: Dict[str, Any]) -> np.ndarray:
        """Calculate rule-based scores for all recipes."""
        scores = np.zeros(len(self.recipes))
        
        for i, recipe in enumerate(self.recipes):
            score = 0.0
            recipe_text = self._recipe_to_text(recipe).lower()
            recipe_title = recipe.get('title', '').lower()
            
            # Dish name matching (highest weight)
            if parsed_query.get('dish_name'):
                dish = parsed_query['dish_name'].lower()
                if dish in recipe_title:
                    score += 0.4
                elif dish in recipe_text:
                    score += 0.2
            
            # Ingredient matching
            if parsed_query.get('ingredients'):
                matched = sum(1 for ing in parsed_query['ingredients'] if ing.lower() in recipe_text)
                if parsed_query['ingredients']:
                    score += 0.3 * (matched / len(parsed_query['ingredients']))
            
            # Category matching
            if parsed_query.get('categories'):
                recipe_cats = str(recipe.get('categories', '')).lower()
                matched = sum(1 for cat in parsed_query['categories'] if cat in recipe_cats or cat in recipe_text)
                if parsed_query['categories']:
                    score += 0.2 * (matched / len(parsed_query['categories']))
            
            # Meal type matching
            if parsed_query.get('meal_type'):
                meal = parsed_query['meal_type'].lower()
                if meal in recipe_text:
                    score += 0.1
            
            scores[i] = score
        
        # Normalize
        if np.max(scores) > 0:
            scores = scores / np.max(scores)
        
        return scores
    
    def _apply_constraints(self, parsed_query: Dict[str, Any]) -> np.ndarray:
        """Apply hard constraints (excluded ingredients and nutrition)."""
        mask = np.ones(len(self.recipes))
        
        excluded = parsed_query.get('excluded_ingredients', [])
        nutrition_req = parsed_query.get('nutrition', {})
        
        for i, recipe in enumerate(self.recipes):
            # Check excluded ingredients
            if excluded:
                recipe_text = self._recipe_to_text(recipe).lower()
                for exc_ing in excluded:
                    if exc_ing.lower() in recipe_text:
                        mask[i] = 0
                        break
            
            # Check nutrition constraints (if recipe already excluded, skip)
            if mask[i] > 0 and nutrition_req:
                if not self._nutrition_matches(recipe, nutrition_req):
                    mask[i] = 0
        
        return mask
    
    def _nutrition_matches(self, recipe: Dict[str, Any], nutrition_req: Dict[str, Any]) -> bool:
        """Check if recipe meets nutritional requirements."""
        for nutrient, constraints in nutrition_req.items():
            recipe_value = recipe.get(nutrient)
            
            # If recipe doesn't have nutrition data, we can't filter - include it
            if recipe_value is None:
                continue
            
            try:
                recipe_value = float(recipe_value)
            except (ValueError, TypeError):
                continue
            
            # Check minimum constraint (for "high protein", "high calorie")
            if 'min' in constraints:
                if recipe_value < constraints['min']:
                    return False
            
            # Check maximum constraint (for "low calorie", "low fat")
            if 'max' in constraints:
                if recipe_value > constraints['max']:
                    return False
        
        return True
    
    def _get_match_reasons(self, recipe: Dict[str, Any], parsed_query: Dict[str, Any]) -> List[str]:
        """Generate human-readable match reasons."""
        reasons = []
        recipe_text = self._recipe_to_text(recipe).lower()
        
        if parsed_query.get('dish_name') and parsed_query['dish_name'].lower() in recipe.get('title', '').lower():
            reasons.append(f"Matches '{parsed_query['dish_name']}' dish type")
        
        if parsed_query.get('ingredients'):
            matched = [ing for ing in parsed_query['ingredients'] if ing.lower() in recipe_text]
            if matched:
                reasons.append(f"Contains: {', '.join(matched[:3])}")
        
        if parsed_query.get('categories'):
            matched = [cat for cat in parsed_query['categories'] if cat in recipe_text]
            if matched:
                reasons.append(f"Category: {', '.join(matched[:2])}")
        
        if not reasons:
            reasons.append("Semantic similarity match")
        
        return reasons
    
    def _safe_number(self, value) -> Optional[float]:
        """Convert value to JSON-serializable number."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific recipe by its index."""
        if 0 <= recipe_id < len(self.recipes):
            recipe = self.recipes[recipe_id].copy()
            recipe['id'] = recipe_id
            return recipe
        return None
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories from the dataset."""
        categories = set()
        for recipe in self.recipes:
            cats = recipe.get('categories', [])
            if isinstance(cats, list):
                categories.update(str(cat) for cat in cats if cat)
            elif cats:
                categories.add(str(cats))
        return sorted(list(categories))
