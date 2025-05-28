from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from shapely import get_coordinates
from app.database import Base


class Zone(Base):
    __tablename__ = 'zones'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    location: WKBElement = Column(Geography(geometry_type="POINT", srid=4326))

    hikes = relationship('Hike', back_populates='zone')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": str(to_shape(self.location).x),
            "lng": str(to_shape(self.location).y)
        }


class Journey(Base):
    __tablename__ = 'journeys'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)

    hikes = relationship('Hike', back_populates='journey')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Trail(Base):
    __tablename__ = 'trails'

    id: int = Column(Integer, primary_key=True)
    gpx: WKBElement = Column(Geography(geometry_type="LINESTRING", srid=4326))

    hikes = relationship('Hike', back_populates='trail')

    def to_dict(self):
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


class Region(Base):
    __tablename__ = 'regions'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)

    hikes = relationship('Hike', back_populates='region')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }








