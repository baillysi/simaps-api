# coding=utf-8

from sqlalchemy import String, Integer, Date, Column, ForeignKey
from sqlalchemy.orm import relationship
import datetime as dt
from dataclasses import dataclass

from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from shapely import get_coordinates
from pyproj import Geod

from model.db import Base


@dataclass
class Zone(Base):
    __tablename__ = 'zones'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    location: WKBElement = Column(Geography(geometry_type="POINT", srid=4326))

    hikes = relationship('Hike', back_populates='zone')

    def __repr__(self):
        return {
            "id": self.id,
            "name": self.name,
            "hikes": [hike.__repr__() for hike in self.hikes],
            "lat": str(to_shape(self.location).x),
            "lng": str(to_shape(self.location).y)
        }


@dataclass
class Journey(Base):
    __tablename__ = 'journeys'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)

    hikes = relationship('Hike', back_populates='journey', lazy='noload')

    def __repr__(self):
        return {
            "id": self.id,
            "name": self.name
        }


@dataclass
class Trail(Base):
    __tablename__ = 'trails'

    id: int = Column(Integer, primary_key=True)
    gpx: WKBElement = Column(Geography(geometry_type="LINESTRING", srid=4326))

    hikes = relationship('Hike', back_populates='trail', lazy='noload')

    def __repr__(self):
        geojson = self.define_geojson()
        return {
            "id": self.id,
            "geojson": geojson
        }

    def define_geojson(self):
        if self.gpx:
            coordinates = get_coordinates(to_shape(self.gpx), include_z=True).tolist()
            geojson = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coordinates
                        },
                        "properties": {
                            "attributeType": "Elevation"
                        }
                    }
                ],
                "properties": {
                    "summary": "Simaps"
                }
            }
        else:
            geojson = None
        return geojson


@dataclass
class Hike(Base):
    __tablename__ = 'hikes'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    distance: int = Column(Integer)
    elevation: int = Column(Integer)
    difficulty: int = Column(Integer)
    duration: int = Column(Integer)
    rates: int = Column(Integer)
    description: str = Column(String)
    created_at = Column(Date, default=dt.datetime.now())

    journey_id = Column(Integer, ForeignKey('journeys.id'), unique=False, nullable=False)
    journey = relationship("Journey", back_populates="hikes")

    zone_id = Column(Integer, ForeignKey('zones.id'), unique=False, nullable=False)
    zone = relationship("Zone", back_populates="hikes")

    trail_id = Column(Integer, ForeignKey('trails.id'), unique=False, nullable=True)
    trail = relationship("Trail", back_populates="hikes")

    def __repr__(self):

        if self.get_geojson_distance():
            distance = round(self.get_geojson_distance() / 1000)
        else:
            distance = self.distance

        if self.get_geojson_elevation():
            elevation = round(self.get_geojson_elevation())
        else:
            elevation = self.elevation

        return {
            "id": self.id,
            "name": self.name,
            "distance": distance,
            "elevation": elevation,
            "difficulty": self.difficulty,
            "duration": self.duration,
            "rates": self.rates,
            "journey": self.journey,
            "description": self.description,
            "trail": self.trail.__repr__(),
        }

    def get_geojson_elevation(self):
        if self.trail:
            coordinates = get_coordinates(to_shape(self.trail.gpx), include_z=True).tolist()
            total_elevation = 0
            for x in range(0, len(coordinates) - 100, 100):
                if (coordinates[x + 100][2]) > (coordinates[x][2]):
                    step = coordinates[x + 100][2] - coordinates[x][2]
                    total_elevation += step
        else:
            total_elevation = None
        return total_elevation

    def get_geojson_distance(self):
        geodesic = Geod(ellps="WGS84")
        if self.trail:
            total_length = geodesic.geometry_length(to_shape(self.trail.gpx))
        else:
            total_length = None
        return total_length








