# coding=utf-8

from sqlalchemy import String, Integer, Date, Column
from sqlalchemy.orm import relationship

from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape

from model.base import Base
from dataclasses import dataclass


@dataclass
class Zone(Base):
    __tablename__ = 'zones'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)

    location: WKBElement = Column(Geography(geometry_type="POINT", srid=4326))

    hikes = relationship('Hike', back_populates='zone', lazy='dynamic')

    def __repr__(self):
        return {
            "id": self.id,
            "name": self.name,
            "hikes": [hike for hike in self.hikes],
            "location": str(to_shape(self.location)),  # cast WKBElement
            "lat": str(to_shape(self.location).x),
            "lng": str(to_shape(self.location).y)
        }






