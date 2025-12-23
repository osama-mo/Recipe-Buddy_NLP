"""
Similarity Engine for Recipe Recommendations
Uses TF-IDF and nutrition-based similarity
"""

import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.models import get_session, Recipe


class SimilarityEngine:
    """
    Find similar recipes based on ingredients, categories, and nutrition.
    
    Uses hybrid approach:
    - TF-IDF for text similarity (ingredients + categories)
    - Euclidean distance for nutrition similarity
    """
    
    def __init__(self):
        """Initialize the similarity engine."""
        self.session = None
        
    def find_similar(self, recipe_id: int, limit: int = 10, 
                    min_score: float = 0.3) -> List[Dict[str, Any]]:
        """
        Find recipes similar to the given recipe.
        
        Args:
            recipe_id: ID of the recipe to find similar recipes for
            limit: Maximum number of similar recipes to return
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of similar recipes with similarity scores
        """
        self.session = get_session()
        
        try:
            # Get the target recipe
            target_recipe = self.session.query(Recipe).filter(Recipe.id == recipe_id).first()
            
            if not target_recipe:
                return []
            
            # Build similarity query
            similar_recipes = self._find_similar_recipes(target_recipe, limit * 3, min_score)
            
            # Format results
            results = []
            for recipe, similarity_score, reasons in similar_recipes[:limit]:
                result = recipe.to_slim_dict()
                result['similarity_score'] = round(similarity_score, 3)
                result['similarity_reasons'] = reasons
                result['nutrition'] = {
                    'calories': recipe.calories or 0,
                    'protein': recipe.protein or 0,
                    'fat': recipe.fat or 0,
                    'sodium': recipe.sodium or 0,
                    'sugar': recipe.sugar or 0,
                    'saturates': recipe.saturates or 0
                }
                results.append(result)
            
            return results
            
        finally:
            if self.session:
                self.session.close()
    
    def _find_similar_recipes(self, target: Recipe, limit: int, 
                            min_score: float) -> List[tuple]:
        """
        Internal method to find similar recipes.
        
        Strategy:
        1. Get candidate recipes with shared ingredients/categories
        2. Calculate text similarity (TF-IDF)
        3. Calculate nutrition similarity
        4. Combine scores and rank
        """
        # Get candidates efficiently
        candidates = self._get_candidate_recipes(target, limit * 10)
        
        if not candidates:
            return []
        
        # Build text corpus for TF-IDF
        target_text = self._recipe_to_text(target)
        candidate_texts = [self._recipe_to_text(r) for r in candidates]
        all_texts = [target_text] + candidate_texts
        
        # Calculate TF-IDF similarity
        vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=1
        )
        
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        text_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        
        # Calculate nutrition similarity
        nutrition_similarities = self._calculate_nutrition_similarity(target, candidates)
        
        # Combine scores (70% text, 30% nutrition)
        combined_scores = 0.7 * text_similarities + 0.3 * nutrition_similarities
        
        # Build results with reasons
        results = []
        for i, recipe in enumerate(candidates):
            if combined_scores[i] >= min_score:
                reasons = self._generate_similarity_reasons(
                    target, recipe, text_similarities[i], nutrition_similarities[i]
                )
                results.append((recipe, combined_scores[i], reasons))
        
        # Sort by similarity score
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def _get_candidate_recipes(self, target: Recipe, limit: int) -> List[Recipe]:
        """
        Get candidate recipes that might be similar.
        
        Uses efficient SQL filtering to reduce search space:
        - Share at least one ingredient keyword
        - Similar nutrition profile (±50% calories)
        - Exclude the target recipe itself
        """
        from sqlalchemy import or_, func
        
        # Extract key ingredients (first 5 main ingredients)
        target_ingredients = target.ingredients[:5] if target.ingredients else []
        
        # Build ingredient search patterns
        ingredient_patterns = []
        for ing in target_ingredients:
            # Extract main ingredient words (skip measurements)
            words = ing.lower().split()
            main_words = [w for w in words if len(w) > 3 and not w[0].isdigit()]
            ingredient_patterns.extend(main_words[:2])
        
        # Remove duplicates
        ingredient_patterns = list(set(ingredient_patterns))[:10]
        
        query = self.session.query(Recipe).filter(Recipe.id != target.id)
        
        # Filter by shared ingredients (using search_text)
        if ingredient_patterns:
            ingredient_filters = [
                func.lower(Recipe.search_text).like(f'%{pattern}%')
                for pattern in ingredient_patterns
            ]
            query = query.filter(or_(*ingredient_filters))
        
        # Filter by similar calorie range (±50%)
        if target.calories and target.calories > 0:
            min_cal = target.calories * 0.5
            max_cal = target.calories * 1.5
            query = query.filter(
                Recipe.calories.between(min_cal, max_cal)
            )
        
        # Get candidates
        candidates = query.limit(limit).all()
        
        return candidates
    
    def _recipe_to_text(self, recipe: Recipe) -> str:
        """Convert recipe to searchable text."""
        parts = []
        
        # Title (weighted heavily)
        if recipe.title:
            parts.extend([recipe.title] * 3)
        
        # Ingredients
        if recipe.ingredients:
            parts.extend(recipe.ingredients[:10])
        
        # Categories
        if recipe.categories:
            parts.extend(recipe.categories)
        
        return ' '.join(parts).lower()
    
    def _calculate_nutrition_similarity(self, target: Recipe, 
                                       candidates: List[Recipe]) -> np.ndarray:
        """
        Calculate nutrition similarity using normalized Euclidean distance.
        
        Considers: calories, protein, fat, sodium
        Returns: Similarity scores (0-1, higher is more similar)
        """
        # Extract nutrition vectors
        target_nutrition = self._get_nutrition_vector(target)
        candidate_nutritions = np.array([
            self._get_nutrition_vector(r) for r in candidates
        ])
        
        # Calculate Euclidean distances
        distances = np.linalg.norm(candidate_nutritions - target_nutrition, axis=1)
        
        # Convert distances to similarities (0-1 scale)
        # Using exponential decay: similarity = exp(-distance / scale)
        scale = 100.0  # Tune this based on typical nutrition ranges
        similarities = np.exp(-distances / scale)
        
        return similarities
    
    def _get_nutrition_vector(self, recipe: Recipe) -> np.ndarray:
        """Get normalized nutrition vector for similarity calculation."""
        return np.array([
            recipe.calories or 0,
            (recipe.protein or 0) * 10,     # Scale protein (grams are smaller than calories)
            (recipe.fat or 0) * 10,         # Scale fat
            (recipe.sodium or 0) / 10       # Scale down sodium (mg are larger)
        ])
    
    def _generate_similarity_reasons(self, target: Recipe, candidate: Recipe,
                                    text_sim: float, nutrition_sim: float) -> List[str]:
        """Generate human-readable reasons for similarity."""
        reasons = []
        
        # Check ingredient overlap
        if target.ingredients and candidate.ingredients:
            target_ings = set([ing.lower() for ing in target.ingredients])
            candidate_ings = set([ing.lower() for ing in candidate.ingredients])
            
            # Find common ingredient keywords
            common_keywords = []
            for t_ing in target_ings:
                for c_ing in candidate_ings:
                    t_words = set(t_ing.split())
                    c_words = set(c_ing.split())
                    common = t_words & c_words
                    # Filter meaningful words
                    common = {w for w in common if len(w) > 3 and not w[0].isdigit()}
                    common_keywords.extend(common)
            
            common_keywords = list(set(common_keywords))[:3]
            if common_keywords:
                reasons.append(f"Shares ingredients: {', '.join(common_keywords)}")
        
        # Check category overlap
        if target.categories and candidate.categories:
            common_cats = set(target.categories) & set(candidate.categories)
            if common_cats:
                reasons.append(f"Similar category: {', '.join(list(common_cats)[:2])}")
        
        # Check nutrition similarity
        if nutrition_sim > 0.7:
            cal_diff = abs((target.calories or 0) - (candidate.calories or 0))
            if cal_diff < 50:
                reasons.append(f"Similar calories (~{int(candidate.calories or 0)} cal)")
            
            prot_diff = abs((target.protein or 0) - (candidate.protein or 0))
            if prot_diff < 5:
                reasons.append(f"Similar protein (~{int(candidate.protein or 0)}g)")
        
        # Generic similarity
        if text_sim > 0.5:
            reasons.append(f"High text similarity ({int(text_sim*100)}%)")
        
        if not reasons:
            reasons.append("Similar recipe profile")
        
        return reasons[:3]  # Max 3 reasons


if __name__ == "__main__":
    # Test the similarity engine
    # Ensure DATABASE_URL is set in your environment before running
    import os
    
    if not os.environ.get('DATABASE_URL'):
        print("ERROR: Set DATABASE_URL environment variable first")
        exit(1)
    
    engine = SimilarityEngine()
    
    # Test with a random recipe
    similar = engine.find_similar(recipe_id=100, limit=5)
    
    print("Similar recipes found:")
    for recipe in similar:
        print(f"\n{recipe['title']} (Score: {recipe['similarity_score']})")
        print(f"  Reasons: {', '.join(recipe['similarity_reasons'])}")
