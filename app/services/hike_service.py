from app.models import Hike
from app.database import Session
from sqlalchemy.orm import joinedload


def get_hike_by_id(hike_id):
    with Session() as session:
        hike = (
            session.query(Hike)
            .options(
                joinedload(Hike.trail),
                joinedload(Hike.region),
                joinedload(Hike.journey),
                joinedload(Hike.zone)
            )
            .filter(Hike.id == hike_id)
            .first()
        )
        return hike.to_dict() if hike else None


def get_hikes(filters=None):
    with Session() as session:
        query = (
            session.query(Hike)
            .options(
                joinedload(Hike.trail),
                joinedload(Hike.region),
                joinedload(Hike.journey),
                joinedload(Hike.zone)
            )
        )
        if filters:
            if "zone_id" in filters:
                query = query.filter(Hike.zone_id == filters['zone_id'])
        hikes = query.all()
        return [hike.to_dict() for hike in hikes]


def update_hike(hike_id, data):
    with Session() as session:
        hike = session.get(Hike, hike_id)
        if not hike:
            return None
        hike.name = data['name']
        hike.distance = data['distance']
        hike.elevation = data['elevation']
        hike.difficulty = data['difficulty']
        hike.duration = data['duration']
        hike.journey_id = data['journey']['id']
        hike.region_id = data['region']['id']
        hike.description = data['description']

        session.commit()
        session.refresh(hike)
        return hike.to_dict()


def create_hike(data):
    with Session() as session:
        new_hike = Hike(
            name=data['name'],
            distance=data['distance'],
            elevation=data['elevation'],
            difficulty=data['difficulty'],
            duration=data['duration'],
            description=data['description'],
        )
        new_hike.journey_id = data['journey']['id']
        new_hike.region_id = data['region']['id']
        new_hike.zone_id = data['zone_id']

        session.add(new_hike)
        session.commit()
        session.refresh(new_hike)
        return new_hike.to_dict()


def delete_hike(hike_id):
    with Session() as session:
        hike = session.get(Hike, hike_id)

        session.delete(hike)
        session.commit()
