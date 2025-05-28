from sqlalchemy import String, Integer, Date, Column, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import datetime as dt
from app.database import Base


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

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "note": self.note,
            "rate": self.rate,
            "created_at": self.created_at.strftime("%d/%m/%y"),
            "is_validated": self.is_validated
        }
