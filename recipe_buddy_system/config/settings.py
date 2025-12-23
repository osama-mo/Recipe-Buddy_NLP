"""
Configuration settings for Recipe Buddy API
"""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Database settings (Neon PostgreSQL)
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_DATABASE = DATABASE_URL is not None

# Fallback JSON path (for local development without DB)
HALAL_RECIPES_PATH = os.path.join(DATA_DIR, 'halal_recipes.json')

# API settings
API_VERSION = "2.1"
API_NAME = "Recipe Buddy API"
DEFAULT_MAX_RESULTS = 20
MAX_RESULTS_LIMIT = 100

# TF-IDF settings (only used if USE_DATABASE is False)
TFIDF_MAX_FEATURES = 1000
TFIDF_NGRAM_RANGE = (1, 1)
TFIDF_MIN_DF = 10
TFIDF_MAX_DF = 0.5

# Scoring weights (V2 Hybrid)
RULE_BASED_WEIGHT = 0.7  # 70% rule-based
TFIDF_WEIGHT = 0.3       # 30% TF-IDF

# Flask settings
DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))
