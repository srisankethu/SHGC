from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///details.db', echo=True)
Base = declarative_base()


class Details(Base):
    """"""
    __tablename__ = "users"

    id = Column(Integer)
    username = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    number = Column(String)
    password = Column(String)

    def __init__(self, username, number, name, email, password):
        self.username = username
        self.name = name
        self.email = email
        self.number = number
        self.password = password

Base.metadata.create_all(engine)
