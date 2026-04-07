import os
import json
import functools
from flask import request
from flask_jwt_extended import get_jwt_identity

try:
    import redis
    _redis_url = os.getenv("REDIS_URL")
    if _redis_url:
        redis_client = redis.from_url(_redis_url, decode_responses=True)
        redis_client.ping()
    else:
        redis_client = None
except Exception:
    redis_client = None


def cached(prefix: str, ttl: int = 60, per_user: bool = False):
    """
    Decorator to cache JSON responses in Redis.
    - prefix: cache key prefix (e.g. 'user_dashboard')
    - ttl: time-to-live in seconds
    - per_user: if True, cache key includes user id
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not redis_client:
                return fn(*args, **kwargs)

            # Build cache key
            parts = [prefix]
            if per_user:
                try:
                    parts.append(f"u:{get_jwt_identity()}")
                except Exception:
                    return fn(*args, **kwargs)

            # Include query params in key
            qs = request.query_string.decode('utf-8')
            if qs:
                parts.append(qs)

            # Include route params
            if kwargs:
                parts.append(str(sorted(kwargs.items())))

            cache_key = ":".join(parts)

            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data), 200
            except Exception:
                pass

            result = fn(*args, **kwargs)

            # Only cache successful (200/201) tuple responses
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
                if status_code in (200, 201):
                    try:
                        redis_client.setex(cache_key, ttl, json.dumps(response_data.get_json()))
                    except Exception:
                        pass

            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """Delete all cache keys matching a pattern."""
    if not redis_client:
        return
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass
