from sqlalchemy import String, Integer, Date, Column, ForeignKey
from sqlalchemy.orm import relationship
import datetime as dt
from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from app.database import Base


class Viewpoint(Base):
    __tablename__ = 'viewpoints'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    created_at = Column(Date, default=dt.datetime.now())
    location: WKBElement = Column(Geography(geometry_type="POINT", srid=4326))

    hike_id = Column(Integer, ForeignKey('hikes.id'), unique=False, nullable=False)
    hike = relationship("Hike", back_populates="viewpoints")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": str(to_shape(self.location).x),
            "lng": str(to_shape(self.location).y)
        }
