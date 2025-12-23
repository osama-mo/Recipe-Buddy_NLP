"""
System API Routes
Handles health check, stats, and documentation endpoints
"""

from flask import Blueprint, jsonify

from config.settings import API_NAME, API_VERSION
from core.cache import get_cache_manager

# Will be injected by app
recipes = None
query_parser = None
recipe_matcher = None
cache = get_cache_manager()


system_bp = Blueprint('system', __name__)


def init_system_routes(recipes_list, parser, matcher):
    """Initialize with app instances."""
    global recipes, query_parser, recipe_matcher
    recipes = recipes_list
    query_parser = parser
    recipe_matcher = matcher


@system_bp.route('/', methods=['GET'])
def home():
    """API home endpoint with documentation."""
    # Get count from metadata or recipes list
    total_count = recipe_matcher.metadata.get('total_recipes', 0) if recipe_matcher else len(recipes)
    
    return jsonify({
        'name': API_NAME,
        'version': API_VERSION,
        'description': 'Intelligent Halal Recipe Search with NLP and ML',
        'total_recipes': total_count,
        'endpoints': {
            'GET /': 'This documentation',
            'GET /health': 'Health check',
            'GET /stats': 'Dataset statistics',
            'POST /search': 'Search recipes with natural language query',
            'GET /search/simple': 'Simple search with query parameter',
            'GET /recipe/<id>': 'Get recipe by ID',
            'GET /random': 'Get random recipes',
            'GET /categories': 'List all categories',
            'GET /ingredients': 'List common ingredients',
            'POST /parse': 'Parse query without searching'
        },
        'example_queries': [
            'chicken without onion',
            'low calorie vegetarian pasta',
            'spicy indian curry with coconut milk',
            'high protein breakfast no eggs'
        ],
        'new_features': {
            'GET /recipes/<id>/similar': 'Find similar recipes',
            'POST /meal-plan': 'Generate personalized meal plans',
            'GET /meal-plan/quick': 'Quick preset meal plans',
            'GET /cache/stats': 'Cache performance statistics'
        }
    })


@system_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    total_count = recipe_matcher.metadata.get('total_recipes', 0) if recipe_matcher else len(recipes)
    
    return jsonify({
        'status': 'healthy',
        'recipes_loaded': total_count,
        'database_mode': recipe_matcher.use_database if recipe_matcher else False,
        'nlp_ready': query_parser is not None,
        'matcher_ready': recipe_matcher is not None
    })


@system_bp.route('/stats', methods=['GET'])
def stats():
    """Get dataset statistics."""
    from config.settings import USE_DATABASE
    
    if USE_DATABASE:
        # Database mode: get stats from metadata
        return jsonify({
            'total_recipes': recipe_matcher.metadata.get('total_recipes', 0),
            'source': 'postgresql',
            'mode': 'database (lazy-load)',
            'features': ['semantic_search', 'nutrition_filtering', 'fuzzy_matching']
        })
    else:
        # JSON mode: compute stats from loaded recipes
        from core.data_loader import get_recipe_stats
        
        if not recipes:
            return jsonify({'error': 'Recipes not loaded'}), 500
        
        return jsonify(get_recipe_stats(recipes))


@system_bp.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Get cache statistics."""
    stats = cache.get_stats()
    
    return jsonify({
        'cache': stats,
        'description': {
            'hits': 'Number of successful cache retrievals',
            'misses': 'Number of cache misses',
            'hit_rate': 'Percentage of requests served from cache',
            'backend': 'Cache backend (redis or memory)',
            'size': 'Number of cached entries (memory mode only)'
        }
    })
