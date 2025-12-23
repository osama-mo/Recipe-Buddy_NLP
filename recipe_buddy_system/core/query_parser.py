"""
NLP Query Parser Module
Extracts structured requirements from natural language queries
"""

import re
import spacy
from typing import Dict, List, Any, Tuple

from config.vocabulary import (
    NEGATION_WORDS, MEAL_TYPES, FOOD_CATEGORIES,
    NUTRITION_KEYWORDS, COMMON_INGREDIENTS, DISH_NAMES
)
from core.spell_corrector import SpellCorrector


class QueryParser:
    """Parse natural language queries to extract recipe requirements."""
    
    def __init__(self):
        """Initialize spaCy model and spell corrector."""
        # Load spaCy English model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy English model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        self.spell_corrector = SpellCorrector()
    
    def parse(self, query: str, correct_spelling: bool = True) -> Dict[str, Any]:
        """
        Parse a natural language query and extract requirements.
        
        Args:
            query: User's search query
            correct_spelling: Whether to apply spell correction
            
        Returns:
            Parsed query with extracted components
        """
        original_query = query
        corrections = []
        
        # Apply spell correction
        if correct_spelling:
            query, corrections = self.spell_corrector.correct(query)
        
        query_lower = query.lower()
        doc = self.nlp(query_lower)
        
        result = {
            'original_query': original_query,
            'corrected_query': query if corrections else None,
            'spelling_corrections': corrections,
            'ingredients': [],
            'excluded_ingredients': [],
            'categories': [],
            'meal_type': None,
            'nutrition': {},
            'dish_name': None
        }
        
        # Extract components
        result['dish_name'] = self._extract_dish_name(query_lower)
        
        included, excluded = self._extract_ingredients(query_lower, doc)
        result['ingredients'] = included
        result['excluded_ingredients'] = excluded
        
        result['meal_type'] = self._extract_meal_type(query_lower)
        result['categories'] = self._extract_categories(query_lower)
        result['nutrition'] = self._extract_nutrition(query_lower)
        
        return result
    
    def _extract_dish_name(self, query: str) -> str:
        """Extract dish name from the query."""
        for dish in DISH_NAMES:
            if dish in query:
                return dish
        return None
    
    def _extract_meal_type(self, query: str) -> str:
        """Extract meal type from the query."""
        for meal_type, keywords in MEAL_TYPES.items():
            for keyword in keywords:
                if keyword in query:
                    return meal_type
        return None
    
    def _extract_categories(self, query: str) -> List[str]:
        """Extract food categories from the query."""
        categories = []
        for category, keywords in FOOD_CATEGORIES.items():
            for keyword in keywords:
                if keyword in query:
                    categories.append(category)
                    break
        return categories
    
    def _extract_ingredients(self, query: str, doc) -> Tuple[List[str], List[str]]:
        """Extract included and excluded ingredients from the query."""
        included = []
        excluded = []
        
        # Words to skip
        skip_words = {
            'meal', 'recipe', 'dish', 'food', 'calorie', 'calories', 'protein',
            'quick', 'easy', 'healthy', 'high', 'low', 'breakfast', 'lunch',
            'dinner', 'vegetarian', 'vegan', 'want', 'need', 'find', 'make'
        }
        skip_words.update(DISH_NAMES)
        
        # Negation patterns - order matters (more specific first)
        negation_patterns = [
            # "doesn't have X", "doesn't include X", "doesn't contain X"
            r"(?:doesn'?t|does\s*not|dont)\s+(?:have|include|contain|want|use|need)\s+(\w+(?:\s+\w+)?)",
            # "don't want X", "don't add X"
            r"(?:don'?t|do\s*not)\s+(?:want|use|add|include|need)\s+(\w+(?:\s+\w+)?)",
            # "but no X", "and no X"
            r"(?:but|and)\s+no\s+(\w+(?:\s+\w+)?)",
            # Standard patterns
            r'without\s+(\w+(?:\s+\w+)?)',
            r'\bno\s+(\w+(?:\s+\w+)?)',
            r'avoid(?:ing)?\s+(\w+(?:\s+\w+)?)',
            r'exclud(?:e|ing)\s+(\w+(?:\s+\w+)?)',
            r'(\w+)[\s-]free\b',
            r'skip(?:ping)?\s+(\w+(?:\s+\w+)?)',
            r'hold\s+(?:the\s+)?(\w+(?:\s+\w+)?)',
            r'minus\s+(\w+(?:\s+\w+)?)',
            r'leave\s+out\s+(\w+(?:\s+\w+)?)',
            r'not?\s+(?:any|the)\s+(\w+(?:\s+\w+)?)',
        ]
        
        # Find excluded ingredients
        for pattern in negation_patterns:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                excluded_item = match.group(1).strip().lower()
                for ing in COMMON_INGREDIENTS:
                    if excluded_item in ing or ing in excluded_item:
                        if ing not in excluded and ing not in skip_words:
                            excluded.append(ing)
        
        # Find included ingredients
        for ingredient in COMMON_INGREDIENTS:
            if ingredient in query and ingredient not in DISH_NAMES:
                # Check if negated
                is_negated = False
                ing_pos = query.find(ingredient)
                context = query[max(0, ing_pos-30):ing_pos].lower()
                
                if any(neg in context for neg in NEGATION_WORDS):
                    is_negated = True
                if ingredient in excluded:
                    is_negated = True
                
                if not is_negated and ingredient not in included:
                    included.append(ingredient)
        
        return (included[:10], excluded[:10])
    
    def _extract_nutrition(self, query: str) -> Dict[str, Any]:
        """Extract nutritional requirements from the query."""
        nutrition = {}
        
        # Numeric constraint patterns
        patterns = [
            (r'at least (\d+)\s*(?:grams?|g)?\s*(?:of\s+)?(protein|fat|sodium)', 'min'),
            (r'at least (\d+)\s*(calories?|cal)', 'min'),
            (r'(?:more than|over)\s*(\d+)\s*(?:grams?|g)?\s*(?:of\s+)?(protein|fat|sodium)', 'min'),
            (r'(?:less than|under)\s*(\d+)\s*(?:grams?|g)?\s*(?:of\s+)?(protein|fat|sodium)', 'max'),
            (r'(?:less than|under)\s*(\d+)\s*(calories?|cal)', 'max'),
        ]
        
        for pattern, constraint_type in patterns:
            for match in re.finditer(pattern, query):
                value = int(match.group(1))
                nutrient = match.group(2).lower()
                
                if 'calorie' in nutrient or 'cal' in nutrient:
                    nutrient = 'calories'
                
                nutrition[nutrient] = {constraint_type: value}
        
        # Modifier-based constraints
        # HIGH modifiers (minimum values)
        if 'high protein' in query or 'high-protein' in query or 'protein rich' in query:
            nutrition.setdefault('protein', {})['min'] = 15
        
        if 'high calorie' in query or 'high-calorie' in query or 'calorie rich' in query:
            nutrition.setdefault('calories', {})['min'] = 400
        
        if 'high fat' in query or 'high-fat' in query:
            nutrition.setdefault('fat', {})['min'] = 15
        
        # LOW modifiers (maximum values)
        if 'low protein' in query or 'low-protein' in query:
            nutrition.setdefault('protein', {})['max'] = 10
        
        if 'low fat' in query or 'low-fat' in query:
            nutrition.setdefault('fat', {})['max'] = 10
        
        if 'low calorie' in query or 'low-calorie' in query or 'light' in query.split():
            nutrition.setdefault('calories', {})['max'] = 300
        
        if 'low sodium' in query or 'low-sodium' in query or 'low salt' in query:
            nutrition.setdefault('sodium', {})['max'] = 400
        
        if 'low sugar' in query or 'low-sugar' in query or 'sugar free' in query:
            nutrition.setdefault('sugar', {})['max'] = 5
        
        return nutrition
