from pydantic import BaseModel
from uuid import UUID
class ImageCollectorAssociationSchema(BaseModel):
    image_id: str
    collector_id: int

class HostImageAssociationSchema(BaseModel):
    host_id: UUID
    image_id: str
