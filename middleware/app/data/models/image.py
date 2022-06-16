from sqlalchemy import Integer, Column, String
from app.data.db.conn import Base
from sqlalchemy.orm import relationship

from app.data.models.associations import collector_image

class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    name = Column('name', String(100))

    collectors = relationship("Collector", secondary = collector_image)

    def __init__(self, name):
        self.name = name
