# coding=utf-8

from sqlalchemy import String, Integer, Date, Column
from sqlalchemy.orm import relationship
from model.base import Base, hosts_hikes_association
import datetime as dt
from dataclasses import dataclass


@dataclass
class Host(Base):
    __tablename__ = 'hosts'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    zone: str = Column(String)
    price: int = Column(Integer)
    created_at = Column(Date, default=dt.datetime.now())

    hikes = relationship("Hike", secondary=hosts_hikes_association, back_populates='hosts')

    def __repr__(self):
        return {
            "id": self.id,
            "name": self.name,
            "zone": self.zone,
            "price": self.price,
            "hikes": [hike for hike in self.hikes]
        }



