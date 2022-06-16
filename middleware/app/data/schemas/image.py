from pydantic import BaseModel
from typing import List

from app.data.schemas.collector import CollectorSchema

class ImageBaseSchema(BaseModel):
    name: str

class ImageBodySchema(ImageBaseSchema):
    pass

class ImageSchema(ImageBaseSchema):
    id: int
    name: str
    collectors: List[CollectorSchema]

    class Config:
        orm_mode = True

