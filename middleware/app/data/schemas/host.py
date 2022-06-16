from pydantic import BaseModel

from app.data.schemas.image import ImageSchema
from uuid import UUID
from typing import Optional

class HostBaseSchema(BaseModel):
    id: UUID
    vim_id: UUID
    hostname: str
    ip: str
    state_id: int
    
class HostBodySchema(HostBaseSchema):
    pass

class HostSchema(HostBaseSchema):
    # image: Optional[ImageSchema]

    class Config:
        orm_mode = True