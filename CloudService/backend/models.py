from pydantic import BaseModel
from datetime import date
from typing import List
from database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String


class Device(Base):
    __tablename__ = 'Devices'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    ip = Column(String)
    category = Column(String)  # Foreign key


class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True)
    info = Column(String)
