# coding=utf-8

from sqlalchemy import String, Integer, Date, Column
from sqlalchemy.orm import relationship
from model.base import Base, hosts_hikes_association
import datetime as dt
from dataclasses import dataclass


@dataclass
class Hike(Base):
    __tablename__ = 'hikes'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    distance: int = Column(Integer)
    created_at = Column(Date, default=dt.datetime.now())

    hosts = relationship("Host", secondary=hosts_hikes_association, back_populates='hikes')

