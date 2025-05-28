from flask import Blueprint, jsonify, request
from app.services import review_service
from app.auth import verify_firebase_token_and_role, get_user_id
from app.logger import logger

review_bp = Blueprint('review_bp', __name__, url_prefix='/api/reviews')


@review_bp.route('')
def get_reviews():
    filters = {}
    hike_id = request.args.get("hike_id")
    logger.info(f"GET request for reviews with hike {hike_id}")
    if hike_id:
        filters["hike_id"] = hike_id
    reviews = review_service.get_reviews(filters=filters)
    logger.info(f"{len(reviews)} reviews retrieved")
    return jsonify(reviews), 200


@review_bp.route('/<int:review_id>', methods=['PUT'])
@verify_firebase_token_and_role
def update_review(review_id):
    data = request.get_json()
    logger.info(f"PUT request to update review with ID {review_id} by user {get_user_id()}")
    updated = review_service.update_review(review_id, data)
    if updated is None:
        logger.warning(f"Review with ID {review_id} not found")
        return jsonify({"error": "Review not found"}), 404
    logger.info(f"Successfully updated review with ID {review_id}")
    return updated, 200


@review_bp.route('', methods=['POST'])
@verify_firebase_token_and_role
def create_review():
    data = request.get_json()
    logger.info(f"POST request to create review with data {data} by user {get_user_id()}")
    try:
        review = review_service.create_review(data)
        logger.info(f"Successfully created review with ID {review['id']}")
        return review, 201
    except Exception as e:
        logger.error(f"Failed to create review: {str(e)}")
        return jsonify({"error": str(e)}), 400


@review_bp.route('/<int:review_id>', methods=['DELETE'])
@verify_firebase_token_and_role
def delete_review(review_id):
    logger.info(f"DELETE request to delete review with ID {review_id} by user {get_user_id()}")
    try:
        review_service.delete_review(review_id)
        logger.info(f"Successfully deleted review with ID {review_id}")
        return '', 204
    except Exception as e:
        logger.error(f"Failed to delete review: {str(e)}")
        return jsonify({"error": str(e)}), 400
