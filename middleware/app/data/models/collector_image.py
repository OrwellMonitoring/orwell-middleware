from sqlalchemy import Integer, Column, String, ForeignKey
from app.data.db.conn import Base
from sqlalchemy.orm import relationship

class CollectorImage(Base):
    __tablename__ = 'collector_image'
    collector_id = Column(Integer, ForeignKey('collector.id'), primary_key=True)
    image_id = Column(String(100), ForeignKey('image.id'), primary_key=True)

    collectors = relationship("Collector", back_populates="images")
    images = relationship("Image", back_populates="collectors")

    def __init__(self, collector_id, image_id):
        self.collector_id = collector_id
        self.image_id = image_id