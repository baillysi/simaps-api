from app.models import Region, Journey, Zone
from app.database import Session


def get_zone_by_id(zone_id):
    with Session() as session:
        zone = (
            session.query(Zone)
            .filter(Zone.id == zone_id)
            .first()
        )
        return zone.to_dict() if zone else None


def get_regions():
    with Session() as session:
        query = (
            session.query(Region)
        )
        regions = query.all()
        return [region.to_dict() for region in regions]


def get_journeys():
    with Session() as session:
        query = (
            session.query(Journey)
        )
        journeys = query.all()
        return [journey.to_dict() for journey in journeys]
