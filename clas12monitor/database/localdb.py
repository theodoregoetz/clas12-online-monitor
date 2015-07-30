from sqlalchemy import Column, Integer, Float, Enum
from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

def initialize_session(engine_init = 'sqlite:///:memory:'):
    engine = create_engine(engine_init)
    Base.metadata.bind = engine
    session = sessionmaker(bind=engine)()
    Base.metadata.creaate_all()
    return session
