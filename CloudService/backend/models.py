from pydantic import BaseModel
from typing import List
from database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String


class DeviceBase(BaseModel):
    name: str | None = None
    ip: str | None = None
    category: str | None = None


class UserBase(BaseModel):
    name: str
    email: str
    info: str


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
