"""Core module initialization"""
from .spell_corrector import SpellCorrector
from .query_parser import QueryParser
from .recipe_matcher import RecipeMatcher
from .data_loader import load_recipes, get_recipe_stats, get_recipe_by_id, search_recipes_db
from .models import Recipe, get_session, get_engine, init_db
