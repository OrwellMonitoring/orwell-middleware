from fastapi import APIRouter, HTTPException

from app.config.settings import config
from app.data.postgres import postgres_manager
from app.data.models.collector import Collector
from app.data.schemas.collector import CollectorSchema, CollectorBodySchema
from app.data.schemas.response import ErrorResponse

from typing import List

router = APIRouter()

@router.get("/collectors", tags=["collectors"], response_model=List[CollectorSchema])
async def get_all_collectors():
    return postgres_manager.get_all(Collector)


@router.get("/collectors/{collector_id}", tags=["collectors"], response_model=CollectorSchema)
async def get_collector_by_id(collector_id: int):
    collector = postgres_manager.get_by_pk(Collector, collector_id)
    if not collector:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="Collector Not Found", code=404)))
    return collector


@router.post("/collectors", tags=["collectors"], response_model=CollectorSchema)
async def create_new_collector(collector: CollectorBodySchema):
    return postgres_manager.save_one(Collector(collector.name, collector.target, collector.port, collector.type_id))

@router.delete("/collectors/{collector_id}", tags=["collectors"], response_model=CollectorSchema)
async def delete_collector_by_id(collector_id: int):
    collector = postgres_manager.delete_by_pk(Collector, collector_id)
    if not collector:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="Collector Not Found", code=404)))
    return collector


@router.put("/collectors", tags=["collectors"], response_model=CollectorSchema)
async def update_collector(collector: CollectorSchema):
    collector = postgres_manager.update_one(Collector, collector)
    if not collector:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="Collector Not Found", code=404)))
    return collector
