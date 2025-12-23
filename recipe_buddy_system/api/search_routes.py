"""
Search API Routes
Handles recipe search endpoints
"""

import time
import os
from flask import Blueprint, request, jsonify
from core.cache import get_cache_manager, CacheManager

# Will be injected by app
query_parser = None
recipe_matcher = None

# Initialize cache
cache = get_cache_manager(redis_url=os.environ.get('REDIS_URL'))

search_bp = Blueprint('search', __name__)


def init_search_routes(parser, matcher):
    """Initialize with parser and matcher instances."""
    global query_parser, recipe_matcher
    query_parser = parser
    recipe_matcher = matcher


@search_bp.route('/search', methods=['POST'])
def search():
    """
    Search recipes with natural language query.
    
    Request Body:
    {
        "query": "chicken without onion",
        "max_results": 20,
        "page": 1,
        "use_tfidf": true
    }
    """
    start_time = time.time()
    
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query parameter'}), 400
    
    query = data['query']
    max_results = min(data.get('max_results', 20), 100)  # Cap at 100
    page = max(data.get('page', 1), 1)  # Minimum page 1
    use_tfidf = data.get('use_tfidf', True)
    
    # Calculate offset for database-level pagination
    offset = (page - 1) * max_results
    
    # Parse and search with proper pagination
    parsed_query = query_parser.parse(query)
    results = recipe_matcher.search(
        parsed_query, 
        max_results=max_results,
        use_tfidf=use_tfidf,
        offset=offset
    )
    
    query_time = (time.time() - start_time) * 1000
    
    # Note: For true total_results, we'd need a count query
    # For now, we indicate if there's potentially more data
    has_next = len(results) == max_results  # If we got full page, there might be more
    
    return jsonify({
        'query': query,
        'parsed_query': parsed_query,
        'results_count': len(results),
        'page': page,
        'per_page': max_results,
        'has_next': has_next,
        'has_prev': page > 1,
        'query_time_ms': round(query_time, 2),
        'results': results
    })


@search_bp.route('/search/simple', methods=['GET'])
def search_simple():
    """
    Simple search with GET request and pagination.
    CACHED: Results are cached for 5 minutes to improve performance.
    
    Query Parameters:
    - q: Search query (required)
    - limit: Max results per page (default: 20, max: 100)
    - page: Page number (default: 1)
    """
    start_time = time.time()
    
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Missing q parameter'}), 400
    
    limit = min(int(request.args.get('limit', 20)), 100)  # Cap at 100
    page = max(int(request.args.get('page', 1)), 1)  # Minimum page 1
    
    # Try cache first
    cache_key = CacheManager.generate_key('search', query=query, limit=limit, page=page)
    cached_result = cache.get(cache_key)
    
    if cached_result:
        cached_result['cached'] = True
        return jsonify(cached_result)
    
    # Calculate offset for database-level pagination
    offset = (page - 1) * limit
    
    parsed_query = query_parser.parse(query)
    
    # Search with proper pagination
    results = recipe_matcher.search(parsed_query, max_results=limit, offset=offset)
    
    query_time = (time.time() - start_time) * 1000
    
    # Indicate if there's potentially more data
    has_next = len(results) == limit
    
    response = {
        'query': query,
        'results_count': len(results),
        'page': page,
        'per_page': limit,
        'has_next': has_next,
        'has_prev': page > 1,
        'query_time_ms': round(query_time, 2),
        'results': results,
        'cached': False
    }
    
    # Cache for 5 minutes (300 seconds)
    cache.set(cache_key, response, ttl=300)
    
    return jsonify(response)


@search_bp.route('/parse', methods=['POST'])
def parse_query():
    """
    Parse a query without searching (for debugging).
    
    Request Body:
    {
        "query": "chicken without onion low calorie"
    }
    """
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query parameter'}), 400
    
    query = data['query']
    parsed = query_parser.parse(query)
    
    return jsonify({
        'query': query,
        'parsed': parsed
    })
