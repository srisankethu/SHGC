from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///traffic.db', echo=True)
Base = declarative_base()


class Traffic(Base):
    """"""
    __tablename__ = "traffic"

    id = Column(Integer, primary_key=True)
    date = Column(String)
    count = Column(Integer)

    def __init__(self, date, count):
        self.date = date
        self.count = count

Base.metadata.create_all(engine)
