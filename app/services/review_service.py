from app.models import Review
from app.database import Session
from sqlalchemy.orm import joinedload


def get_reviews(filters=None):
    with Session() as session:
        query = (
            session.query(Review)
            .options(
                joinedload(Review.hike)
            )
        )
        if filters:
            if "hike_id" in filters:
                query = query.filter(Review.hike_id == filters['hike_id'])
        reviews = query.all()
        return [review.to_dict() for review in reviews]


def update_review(review_id, data):
    with Session() as session:
        review = session.get(Review, review_id)
        if not review:
            return None
        review.is_validated = data['is_validated']

        session.commit()
        session.refresh(review)
        return review.to_dict()


def create_review(data):
    with Session() as session:
        new_review = Review(
            title=data['title'],
            note=data['note'],
            rate=data['rate'],
        )
        new_review.hike_id = data['hike_id']
        new_review.is_validated = False

        session.add(new_review)
        session.commit()
        session.refresh(new_review)
        return new_review.to_dict()


def delete_review(review_id):
    with Session() as session:
        review = session.get(Review, review_id)

        session.delete(review)
        session.commit()
