"""
Database Models for Recipe Buddy
SQLAlchemy models for PostgreSQL (Neon)
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
import os

Base = declarative_base()


class Recipe(Base):
    """Recipe model - stores all recipe data."""
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Store as arrays for easy querying
    ingredients = Column(ARRAY(Text))
    directions = Column(ARRAY(Text))
    categories = Column(ARRAY(String(100)))
    
    # Nutrition info (per serving or per 100g)
    calories = Column(Float, default=0, index=True)
    protein = Column(Float, default=0, index=True)
    fat = Column(Float, default=0, index=True)
    sodium = Column(Float, default=0)
    sugar = Column(Float, default=0)
    saturates = Column(Float, default=0)
    
    # For full-text search (pre-computed searchable text)
    search_text = Column(Text)
    
    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            'id': self.id,
            'title': self.title,
            'desc': self.description or self.title,
            'ingredients': self.ingredients or [],
            'directions': self.directions or [],
            'categories': self.categories or [],
            'calories': self.calories or 0,
            'protein': self.protein or 0,
            'fat': self.fat or 0,
            'sodium': self.sodium or 0,
            'sugar': self.sugar or 0,
            'saturates': self.saturates or 0,
        }
    
    def to_slim_dict(self):
        """Convert to slim dictionary for search results."""
        return {
            'id': self.id,
            'title': self.title,
            'desc': (self.description or self.title)[:150],
            'ingredients': (self.ingredients or [])[:10],
            'directions': (self.directions or [])[:3],
            'categories': (self.categories or [])[:5],
            'calories': self.calories or 0,
            'protein': self.protein or 0,
            'fat': self.fat or 0,
            'sodium': self.sodium or 0,
            'sugar': self.sugar or 0,
            'saturates': self.saturates or 0,
        }


# Database connection management
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Neon requires SSL
        if 'sslmode' not in database_url:
            database_url += '?sslmode=require'
        
        _engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False
        )
    return _engine


def get_session():
    """Get database session."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()


def init_db():
    """Initialize database tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✅ Database tables created")


def close_db():
    """Close database connections."""
    global _engine, _SessionLocal
    if _engine:
        _engine.dispose()
        _engine = None
        _SessionLocal = None
