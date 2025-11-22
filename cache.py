import json
import os
from typing import Optional
from redis import asyncio as aioredis

# Redis connection URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Cache TTL (Time To Live) in seconds
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # Default: 5 minutes

# Redis client instance
redis_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> aioredis.Redis:
    """Get or create Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_cache(key: str) -> Optional[str]:
    """Get value from cache"""
    try:
        client = await get_redis_client()
        value = await client.get(key)
        return value
    except Exception as e:
        print(f"Cache get error: {e}")
        return None


async def set_cache(key: str, value: str, ttl: int = CACHE_TTL) -> bool:
    """Set value in cache with TTL"""
    try:
        client = await get_redis_client()
        await client.setex(key, ttl, value)
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False


async def delete_cache(key: str) -> bool:
    """Delete value from cache"""
    try:
        client = await get_redis_client()
        await client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False


async def delete_cache_pattern(pattern: str) -> bool:
    """Delete all keys matching pattern"""
    try:
        client = await get_redis_client()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
        return True
    except Exception as e:
        print(f"Cache delete pattern error: {e}")
        return False


async def clear_all_cache() -> bool:
    """Clear all cache"""
    try:
        client = await get_redis_client()
        await client.flushdb()
        return True
    except Exception as e:
        print(f"Cache clear error: {e}")
        return False
