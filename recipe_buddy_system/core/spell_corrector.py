"""
Spell Correction Module (V2 Feature)
Handles typos in user queries
"""

from typing import List, Tuple
from spellchecker import SpellChecker
from config.vocabulary import SPELL_CHECK_WORDS


class SpellCorrector:
    """
    Spell correction for recipe queries.
    
    Fixes typos like:
    - "chiken" → "chicken"
    - "recipie" → "recipe"
    - "tomatoe" → "tomato"
    """
    
    def __init__(self):
        """Initialize spell checker with food vocabulary."""
        self.spell = SpellChecker()
        self.spell.word_frequency.load_words(SPELL_CHECK_WORDS)
    
    def correct(self, query: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Correct spelling in a query.
        
        Args:
            query: User's raw query text
            
        Returns:
            (corrected_query, list of (original, corrected) pairs)
        """
        words = query.split()
        corrected_words = []
        corrections = []
        
        for word in words:
            clean_word = word.lower().strip('.,!?')
            
            # Skip very short words or numbers
            if len(clean_word) <= 2 or clean_word.isdigit():
                corrected_words.append(word)
                continue
            
            # Check if misspelled
            if clean_word in self.spell:
                corrected_words.append(word)
            else:
                corrected = self.spell.correction(clean_word)
                if corrected and corrected != clean_word:
                    corrected_words.append(corrected)
                    corrections.append((word, corrected))
                else:
                    corrected_words.append(word)
        
        return ' '.join(corrected_words), corrections
    
    def suggest(self, word: str, max_suggestions: int = 3) -> List[str]:
        """
        Get spelling suggestions for a word.
        
        Args:
            word: Word to get suggestions for
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested corrections
        """
        candidates = self.spell.candidates(word.lower())
        if candidates:
            return list(candidates)[:max_suggestions]
        return []
