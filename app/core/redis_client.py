import redis.asyncio as aioredis
from app.core.config import settings

redis_client: aioredis.Redis = None

async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
    return redis_client
