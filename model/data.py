# coding=utf-8

from sqlalchemy import String, Integer, Date, Column, ForeignKey, Float, Boolean
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

    hikes = relationship('Hike', back_populates='journey')

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

    hikes = relationship('Hike', back_populates='trail')

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
    distance: float = Column(Float)
    elevation: int = Column(Integer)
    difficulty: int = Column(Integer)
    duration: int = Column(Integer)
    description: str = Column(String)
    created_at = Column(Date, default=dt.datetime.now())

    journey_id = Column(Integer, ForeignKey('journeys.id'), unique=False, nullable=False)
    journey = relationship("Journey", back_populates="hikes")

    zone_id = Column(Integer, ForeignKey('zones.id'), unique=False, nullable=False)
    zone = relationship("Zone", back_populates="hikes")

    region_id = Column(Integer, ForeignKey('regions.id'), unique=False, nullable=False)
    region = relationship("Region", back_populates="hikes")

    trail_id = Column(Integer, ForeignKey('trails.id'), unique=False, nullable=True)
    trail = relationship("Trail", back_populates="hikes")

    reviews = relationship('Review', back_populates='hike')

    viewpoints = relationship('Viewpoint', back_populates='hike')

    def __repr__(self):

        if self.get_geojson_distance():
            distance = round(self.get_geojson_distance() / 1000, 1)
        else:
            distance = round(self.distance, 1)

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
            "journey": self.journey,
            "description": self.description,
            "trail": self.trail.__repr__(),
            "region": self.region.__repr__(),
            "zone": self.zone.name,
        }

    def get_geojson_elevation(self):
        if self.trail:
            coordinates = get_coordinates(to_shape(self.trail.gpx), include_z=True).tolist()
            total_elevation = 0
            for x in range(0, len(coordinates) - 10, 10):
                if (coordinates[x + 10][2]) > (coordinates[x][2]):
                    step = coordinates[x + 10][2] - coordinates[x][2]
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


@dataclass
class Viewpoint(Base):
    __tablename__ = 'viewpoints'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    created_at = Column(Date, default=dt.datetime.now())
    location: WKBElement = Column(Geography(geometry_type="POINT", srid=4326))

    hike_id = Column(Integer, ForeignKey('hikes.id'), unique=False, nullable=False)
    hike = relationship("Hike", back_populates="viewpoints")

    def __repr__(self):

        return {
            "id": self.id,
            "name": self.name,
            "lat": str(to_shape(self.location).x),
            "lng": str(to_shape(self.location).y)
        }


@dataclass
class Region(Base):
    __tablename__ = 'regions'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)

    hikes = relationship('Hike', back_populates='region')

    def __repr__(self):

        return {
            "id": self.id,
            "name": self.name
        }


@dataclass
class Review(Base):
    __tablename__ = 'reviews'

    id: int = Column(Integer, primary_key=True)
    title: str = Column(String)
    note: str = Column(String)
    rate: int = Column(Integer)
    created_at = Column(Date, default=dt.datetime.now())
    is_validated = Column(Boolean)

    hike_id = Column(Integer, ForeignKey('hikes.id'), unique=False, nullable=False)
    hike = relationship("Hike", back_populates="reviews")

    def __repr__(self):

        return {
            "id": self.id,
            "title": self.title,
            "note": self.note,
            "rate": self.rate,
            "created_at": self.created_at.strftime("%d/%m/%y"),
            "is_validated": self.is_validated,
            "hike": self.hike.__repr__()
        }








