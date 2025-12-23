"""
Caching Layer for Recipe Buddy
Supports both Redis and in-memory caching
"""

import json
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta
from functools import wraps


class CacheManager:
    """
    Flexible caching manager supporting Redis and in-memory fallback.
    
    Features:
    - Automatic Redis detection
    - In-memory fallback when Redis unavailable
    - TTL support
    - Cache key generation
    """
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL (optional)
            default_ttl: Default TTL in seconds (default: 1 hour)
        """
        self.default_ttl = default_ttl
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0, 'sets': 0}
        
        # Try to connect to Redis
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                print("✅ Connected to Redis cache")
            except Exception as e:
                print(f"⚠️  Redis unavailable ({e}), using in-memory cache")
                self.redis_client = None
        else:
            print("✅ Using in-memory cache (set REDIS_URL for Redis)")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if self.redis_client:
                # Try Redis first
                value = self.redis_client.get(key)
                if value:
                    self.cache_stats['hits'] += 1
                    return json.loads(value)
                else:
                    self.cache_stats['misses'] += 1
                    return None
            else:
                # Use memory cache
                if key in self.memory_cache:
                    entry = self.memory_cache[key]
                    # Check if expired
                    if entry['expires_at'] > datetime.now():
                        self.cache_stats['hits'] += 1
                        return entry['value']
                    else:
                        # Expired, remove
                        del self.memory_cache[key]
                        self.cache_stats['misses'] += 1
                        return None
                else:
                    self.cache_stats['misses'] += 1
                    return None
        except Exception as e:
            print(f"Cache get error: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            ttl = ttl or self.default_ttl
            
            if self.redis_client:
                # Use Redis
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
            else:
                # Use memory cache
                self.memory_cache[key] = {
                    'value': value,
                    'expires_at': datetime.now() + timedelta(seconds=ttl)
                }
                
                # Clean up expired entries (max 1000 entries)
                if len(self.memory_cache) > 1000:
                    self._cleanup_memory_cache()
            
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def _cleanup_memory_cache(self):
        """Remove expired entries from memory cache."""
        now = datetime.now()
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if v['expires_at'] <= now
        ]
        for key in expired_keys:
            del self.memory_cache[key]
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'sets': self.cache_stats['sets'],
            'hit_rate': round(hit_rate, 2),
            'backend': 'redis' if self.redis_client else 'memory',
            'size': len(self.memory_cache) if not self.redis_client else 'N/A'
        }
    
    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from arguments.
        
        Example:
            generate_key('search', query='chicken', limit=10)
            -> 'search:abc123def456'
        """
        # Combine all arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = ':'.join(key_parts)
        
        # Hash for consistent length
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]
        
        return f"{prefix}:{key_hash}"


# Global cache instance
_cache_manager = None


def get_cache_manager(redis_url: Optional[str] = None) -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(redis_url=redis_url)
    return _cache_manager


def cached(prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    
    Usage:
        @cached('search', ttl=300)
        def search_recipes(query, limit=10):
            # expensive operation
            return results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Generate cache key
            cache_key = CacheManager.generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test the cache manager
    cache = CacheManager()
    
    # Test set/get
    cache.set('test_key', {'data': 'hello world'}, ttl=10)
    value = cache.get('test_key')
    print(f"Cached value: {value}")
    
    # Test stats
    print(f"Cache stats: {cache.get_stats()}")
    
    # Test decorator
    @cached('expensive_op', ttl=5)
    def expensive_operation(x, y):
        print(f"Computing {x} + {y}...")
        return x + y
    
    print(expensive_operation(5, 3))  # Computes
    print(expensive_operation(5, 3))  # From cache
    print(cache.get_stats())
