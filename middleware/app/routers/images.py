from fastapi import APIRouter, HTTPException

from typing import List

from app.config.settings import config
from app.data.postgres import postgres_manager
from app.data.models.image import Image
from app.data.models.collector import Collector
from app.data.schemas.image import ImageSchema, ImageBodySchema
from app.data.schemas.response import ErrorResponse

from app.data.schemas.associations import ImageCollectorAssociationSchema

router = APIRouter()

@router.get("/images", tags=["images"], response_model=List[ImageSchema])
async def get_all_os_images():
    return postgres_manager.get_all(Image)


@router.get("/images/{image_id}", tags=["images"], response_model=ImageSchema)
async def get_os_image_by_id(image_id: str):
    image = postgres_manager.get_by_pk(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="OS Image Not Found", code=404)))
    return image


@router.post("/images", tags=["images"], response_model=ImageSchema)
async def create_new_os_image(image: ImageBodySchema):
    return postgres_manager.save_one(Image(image.name))

@router.delete("/images/{image_id}", tags=["images"], response_model=ImageSchema)
async def delete_os_image_by_id(image_id: int):
    try:
        image = postgres_manager.delete_by_pk(Image, image)
    except:
        raise HTTPException(status_code=400, detail=dict(ErrorResponse(error="OS Image in use by one or more Hosts", code=400)))
    if not image:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="OS Image Not Found", code=404)))
    return image


@router.put("/images", tags=["images"], response_model=ImageSchema)
async def update_os_image(image: ImageSchema):
    image = postgres_manager.update_one(Image, image)
    if not image:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="OS Image Not Found", code=404)))
    return image

@router.post("/images/collector", tags=["images"], response_model=ImageSchema)
async def add_collector_to_os_images(association: ImageCollectorAssociationSchema):
    image = postgres_manager.get_by_pk(Image, association.image_id)
    collector = postgres_manager.get_by_pk(Collector, association.collector_id)
    if not image or not collector:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="OS Image or Collector Not Found", code=404)))
    
    image.collectors.append(collector)
    return postgres_manager.save_one(image)
