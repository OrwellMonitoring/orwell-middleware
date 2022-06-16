from pydantic import BaseModel


class CollectorTypeBaseSchema(BaseModel):
    name: str

class CollectorTypeSchema(CollectorTypeBaseSchema):
    id: int

    class Config:
        orm_mode = True

