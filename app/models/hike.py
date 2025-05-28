import datetime as dt
from sqlalchemy import String, Integer, Date, Column, ForeignKey, Float
from sqlalchemy.orm import relationship
from geoalchemy2.shape import to_shape
from shapely import get_coordinates
from pyproj import Geod
from app.database import Base


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

    def to_dict(self):
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
            "description": self.description,
            "journey": self.journey.to_dict(),
            "trail": self.trail.to_dict() if self.trail else None,
            "region": self.region.to_dict(),
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



