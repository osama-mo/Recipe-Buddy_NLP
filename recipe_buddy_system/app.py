#!/usr/bin/env python3
"""
Recipe Buddy API - Main Application
Flask REST API for intelligent recipe search
"""

import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS

from config.settings import DEBUG, HOST, PORT, API_NAME, API_VERSION
from core import load_recipes, QueryParser, RecipeMatcher
from api import (
    search_bp, init_search_routes,
    recipe_bp, init_recipe_routes,
    system_bp, init_system_routes,
    features_bp, init_features_routes
)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)
    
    # Load data and initialize components
    recipes, metadata = initialize_components()
    
    # Store in app config for access
    app.config['recipes'] = recipes
    app.config['metadata'] = metadata
    
    # Register blueprints
    app.register_blueprint(system_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(features_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def initialize_components():
    """Load data and initialize NLP/ML components."""
    print("=" * 60)
    print(f"{API_NAME} v{API_VERSION} - Starting Up")
    print("=" * 60)
    
    # Load recipes
    recipes, metadata = load_recipes()
    
    # Initialize NLP processor
    print("\nInitializing NLP processor...")
    query_parser = QueryParser()
    print("✅ NLP processor ready")
    
    # Initialize recipe matcher
    print("\nInitializing Recipe Matcher with TF-IDF...")
    recipe_matcher = RecipeMatcher(recipes, metadata)
    print("✅ Recipe matcher ready")
    
    # Initialize route modules
    init_search_routes(query_parser, recipe_matcher)
    init_recipe_routes(recipes, recipe_matcher)
    init_system_routes(recipes, query_parser, recipe_matcher)
    init_features_routes()
    
    print("\n" + "=" * 60)
    print(f"{API_NAME} - Ready to serve requests!")
    print("=" * 60 + "\n")
    
    return recipes, metadata


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def server_error(e):
        return {'error': 'Internal server error'}, 500


# Create app instance
app = create_app()


if __name__ == '__main__':
    print(f"\n🚀 Starting Flask server...")
    print(f"   Local:   http://127.0.0.1:{PORT}")
    print(f"   Network: http://{HOST}:{PORT}")
    print(f"\n📖 API Documentation: http://127.0.0.1:{PORT}/")
    print("=" * 60 + "\n")
    
    app.run(host=HOST, port=PORT, debug=DEBUG)
