import redis.asyncio as redis
from app.db.session import settings

print("Redis URL:", settings.REDIS_DB_URL)

redis_client = redis.from_url(settings.REDIS_DB_URL, decode_responses=True)


async def get_redis_client():
    return redis_client
