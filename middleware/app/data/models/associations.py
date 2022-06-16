from sqlalchemy import Table, Column, ForeignKey
from app.data.db.conn import Base

collector_image = Table('collector_image', Base.metadata,
    Column('collector_id', ForeignKey('collector.id'), primary_key=True),
    Column('image_id', ForeignKey('image.id'), primary_key=True)
)