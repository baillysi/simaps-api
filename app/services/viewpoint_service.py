from app.models import Viewpoint
from app.database import Session
from sqlalchemy.orm import joinedload


def get_viewpoints(filters=None):
    with Session() as session:
        query = (
            session.query(Viewpoint)
            .options(
                joinedload(Viewpoint.hike)
            )
        )
        if filters:
            if "hike_id" in filters:
                query = query.filter(Viewpoint.hike_id == filters['hike_id'])
        viewpoints = query.all()
        return [viewpoint.to_dict() for viewpoint in viewpoints]
