# coding=utf-8

from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import relationship

from model.db import Base
from dataclasses import dataclass


@dataclass
class Journey(Base):
    __tablename__ = 'journeys'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)

    hikes = relationship('Hike', back_populates='journey', lazy='dynamic')

    def __repr__(self):
        return {
            "id": self.id,
            "name": self.name,
            "hikes": [hike.__repr__() for hike in self.hikes]
        }






