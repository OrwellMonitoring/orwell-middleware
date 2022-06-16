from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import config

engine = create_engine(f'postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:5432/{config.POSTGRES_DB}')

Session = sessionmaker(bind=engine)

session = Session()

Base = declarative_base(engine)

