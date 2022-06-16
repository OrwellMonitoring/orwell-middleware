from fastapi import APIRouter
from app.data.postgres import postgres_manager

from app.data.models.image import Image
from app.data.models.collector_type import CollectorType
from app.data.models.collector import Collector

router = APIRouter()

@router.get("/db/insert", tags=["db"])
async def insert():
    c = collectors()
    i= images()
    t = types()

    postgres_manager.save_all(i)
    postgres_manager.save_all(t)
    postgres_manager.save_all(c)

    return None

@router.get("/db/flush", tags=["db"])
async def flush():
    postgres_manager.flush()

def images():
    return [
        Image("ubuntu-telegraf"),
        Image("ubuntu-prometheus")
    ]

def types():
    return [
        CollectorType("PUSH"),
        CollectorType("PULL")
    ]

def collectors():
    return [
        Collector("telegraf", None, None, 1)
    ]
