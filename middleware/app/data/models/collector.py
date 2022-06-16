from sqlalchemy import Integer, Column, String, ForeignKey
from app.data.db.conn import Base

class Collector(Base):
    __tablename__ = 'collector'
    id = Column(Integer, primary_key=True)
    name = Column('name', String(100))
    target = Column('target', String(100))
    port = Column('port', Integer)
    type_id = Column('type_id', ForeignKey('collector_type.id'))

    def __init__(self, name, target, port, type_id):
        self.name = name
        self.target = target
        self.port = port
        self.type_id = type_id