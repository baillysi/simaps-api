# coding=utf-8

from sqlalchemy import String, Integer, Date, Column, ForeignKey
from sqlalchemy.orm import relationship
from model.base import Base, hosts_hikes_association
import datetime as dt
from dataclasses import dataclass

from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from shapely import get_coordinates
from shapely.ops import transform


@dataclass
class Hike(Base):
    __tablename__ = 'hikes'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    distance: int = Column(Integer)
    created_at = Column(Date, default=dt.datetime.now())

    zone_id = Column(Integer, ForeignKey('zones.id'), unique=False, nullable=False)
    zone = relationship("Zone", back_populates="hikes")

    hosts = relationship('Host', secondary=hosts_hikes_association, back_populates='hikes')

    gpx: WKBElement = Column(Geography(geometry_type="LINESTRING", srid=4326))

    def __repr__(self):
        swapped = transform(lambda x, y: (y, x), to_shape(self.gpx))  # flip lat lng to fit leaflet system
        return {
            "id": self.id,
            "name": self.name,
            "distance": self.distance,
            "coordinates": get_coordinates(swapped).tolist()
        }

