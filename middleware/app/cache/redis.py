import redis
from app.config.settings import config

class RedisManager:
    def __init__(self):
        self._redis = redis.Redis(
            host = config.REDIS_HOST,
            password = config.REDIS_PASSWORD
        )


redis_manager = RedisManager()