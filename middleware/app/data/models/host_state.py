from sqlalchemy import Integer, Column, String, ForeignKey
from app.data.db.conn import Base

class HostState(Base):
    __tablename__ = 'host_state'
    id = Column(Integer, primary_key=True)
    name = Column('name', String(100))

    def __init__(self, name):
        self.name = name