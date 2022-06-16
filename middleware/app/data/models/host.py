from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.data.db.conn import Base
from app.data.models.image import Image
from app.data.models.host_state import HostState

class Host(Base):
    __tablename__ = 'host'
    id = Column(UUID(as_uuid=True), primary_key=True)
    vim_id = Column('vim_id', UUID(as_uuid=True))
    hostname = Column('hostname', String(100))
    ip = Column('ip', String(100))
    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship("Image")
    state_id = Column(Integer, ForeignKey('host_state.id'))
    #state = relationship("HostState")

    def __init__(self, id, vim_id, hostname, ip, image_id=None, state_id=None):
        self.id = id
        self.vim_id = vim_id
        self.hostname = hostname
        self.ip = ip
        self.image_id = image_id
        self.state_id = state_id