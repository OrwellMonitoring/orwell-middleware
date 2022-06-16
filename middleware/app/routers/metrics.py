from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

import redis
from app.config.settings import config
from app.data.postgres import postgres_manager

from app.data.models.image import Image


router = APIRouter()

@router.get("/metrics/{id}", tags=["metrics"])
async def fetch_metrics_by_VNF_id(id: str):
    conn = redis.Redis(
        host = config.REDIS_HOST,
        password = config.REDIS_PASSWORD
    )

    pipe = conn.pipeline()

    pipe.lrange(id, 0, -1)
    pipe.delete(id)

    result = '\n'.join([msg.decode() for msg in pipe.execute()[0]])

    pipe.close()

    conn.close()

    return PlainTextResponse(result)

@router.get("/metrics", tags=["metrics"])
async def fetch_all_metrics():
    conn = redis.Redis(
        host = config.REDIS_HOST,
        password = config.REDIS_PASSWORD
    )

    pipe = conn.pipeline()

    pipe.lrange("METRICS", 0, -1)
    pipe.delete("METRICS")

    result = '\n'.join([msg.decode() for msg in pipe.execute()[0]])

    pipe.close()

    conn.close()

    return PlainTextResponse(result)
        