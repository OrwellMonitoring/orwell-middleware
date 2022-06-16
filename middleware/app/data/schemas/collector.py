from typing import Optional

from app.data.schemas.collector_type import CollectorTypeSchema

from pydantic import BaseModel


class CollectorBaseSchema(BaseModel):
    name: str

class CollectorBodySchema(CollectorBaseSchema):
    target: Optional[str]
    port: int
    type_id: int

class CollectorSchema(CollectorBaseSchema):
    id: int
    target: Optional[str]
    port: int
    type_id: int

    class Config:
        orm_mode = True

