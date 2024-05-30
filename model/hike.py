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
from pyproj import Geod


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

    hosts = relationship('Host', secondary=hosts_hikes_association, back_populates='hikes')

    gpx: WKBElement = Column(Geography(geometry_type="LINESTRING", srid=4326))

    def __repr__(self):
        # TODO handle not null constraint on gpx data
        # PostGIS command to upload gpx to DB :
        # update main.hikes set gpx = ST_SetSRID(ST_MakeLine( ARRAY( SELECT ST_MakePoint(
        # ST_X(ST_GeomFromEWKB(wkb_geometry)),
        # ST_Y(ST_GeomFromEWKB(wkb_geometry)),
        # ele) FROM main.track_points ORDER BY ogc_fid
        # ) ),4326) where id = 53;
        geojson = self.define_geojson()

        if self.get_geojson_distance():
            distance = round(self.get_geojson_distance() / 1000, 1)
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
            "geojson": geojson,
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

    def get_geojson_elevation(self):
        if self.gpx:
            coordinates = get_coordinates(to_shape(self.gpx), include_z=True).tolist()
            x = 1
            total_elevation = 0
            for x in range(len(coordinates)):
                if (coordinates[x][2]) > (coordinates[x - 1][2]):
                    step = coordinates[x][2] - coordinates[x - 1][2]
                    total_elevation += step
        else:
            total_elevation = None
        return total_elevation

    def get_geojson_distance(self):
        geodesic = Geod(ellps="WGS84")
        if self.gpx:
            total_length = geodesic.geometry_length(to_shape(self.gpx))
        else:
            total_length = None
        return total_length








