from fastapi import APIRouter, HTTPException

from app.config.settings import config
from app.data.postgres import postgres_manager
from app.data.models.host import Host
from app.data.models.image import Image
from app.data.schemas.host import HostSchema, HostBodySchema
from app.data.schemas.response import ErrorResponse

from app.data.schemas.associations import HostImageAssociationSchema

from typing import List

router = APIRouter()

@router.get("/hosts", tags=["hosts"], response_model=List[HostSchema])
async def get_all_hosts():
    return postgres_manager.get_all(Host)


@router.get("/hosts/{host_id}", tags=["hosts"], response_model=HostSchema)
async def get_host_by_id(host_id: int):
    host = postgres_manager.get_by_pk(Host, host_id)
    if not host:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="Host Not Found", code=404)))
    return host


@router.post("/hosts", tags=["hosts"], response_model=HostSchema)
async def create_new_host(host: HostBodySchema):
    return postgres_manager.save_one(Host(host.id, host.vim_id, host.hostname, host.ip))

@router.delete("/hosts/{host_id}", tags=["hosts"], response_model=HostSchema)
async def delete_host_by_id(host_id: int):
    host = postgres_manager.delete_by_pk(Host, host_id)
    if not host:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="Host Not Found", code=404)))
    return host


@router.put("/hosts", tags=["hosts"], response_model=HostSchema)
async def update_host(host: HostSchema):
    host = postgres_manager.update_one(Host, host)
    if not host:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="Host Not Found", code=404)))
    return host

@router.post("/hosts/image", response_model=HostSchema)
async def associate_host_with_image(association: HostImageAssociationSchema):
    host = postgres_manager.get_by_pk(Host, association.host_id)
    image = postgres_manager.get_by_pk(Image, association.image_id)
    if not image or not host:
        raise HTTPException(status_code=404, detail=dict(ErrorResponse(error="OS Image or Host Not Found", code=404)))
    
    host.image = image
    return postgres_manager.save_one(host)
