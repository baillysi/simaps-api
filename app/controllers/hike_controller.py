from flask import Blueprint, jsonify, request
from app.services import hike_service
from app.auth import verify_firebase_token_and_role, get_user_role, get_user_id
from app.limiter import limiter
from app.logger import logger

hike_bp = Blueprint('hike_bp', __name__, url_prefix='/api/hikes')


@hike_bp.route('/<int:hike_id>')
def get_hike(hike_id):
    logger.info(f"GET request for hike with ID {hike_id}")
    hike = hike_service.get_hike_by_id(hike_id)
    if not hike:
        logger.warning(f"Hike with ID {hike_id} not found")
        return jsonify({'error': 'Hike not found'}), 404
    logger.info(f"Hike with ID {hike_id} found")
    return hike, 200


@hike_bp.route('')
@limiter.limit(lambda: "100/minute" if get_user_role() == "admin" else "5/minute")
def get_hikes():
    filters = {}
    zone_id = request.args.get("zone_id")
    logger.info(f"GET request for hikes in zone {zone_id}")
    if zone_id:
        filters["difficulty"] = zone_id
    hikes = hike_service.get_hikes(filters=filters)
    logger.info(f"{len(hikes)} hikes retrieved")
    return jsonify(hikes), 200


@hike_bp.route('/<int:hike_id>', methods=['PUT'])
@verify_firebase_token_and_role
def update_hike(hike_id):
    data = request.get_json()
    logger.info(f"PUT request to update hike with ID {hike_id} by user {get_user_id()}")
    updated = hike_service.update_hike(hike_id, data)
    if updated is None:
        logger.warning(f"Hike with ID {hike_id} not found")
        return jsonify({"error": "Hike not found"}), 404
    logger.info(f"Successfully updated hike with ID {hike_id}")
    return updated, 200


@hike_bp.route('', methods=['POST'])
@verify_firebase_token_and_role
def create_hike():
    data = request.get_json()
    logger.info(f"POST request to create with data {data} hike by user {get_user_id()}")
    try:
        hike = hike_service.create_hike(data)
        logger.info(f"Successfully created hike with ID {hike['id']}")
        return hike, 201
    except Exception as e:
        logger.error(f"Failed to create hike: {str(e)}")
        return jsonify({"error": str(e)}), 400


@hike_bp.route('/<int:hike_id>', methods=['DELETE'])
@verify_firebase_token_and_role
def delete_hike(hike_id):
    logger.info(f"DELETE request to delete hike with ID {hike_id} by user {get_user_id()}")
    try:
        hike_service.delete_hike(hike_id)
        logger.info(f"Successfully deleted hike with ID {hike_id}")
        return '', 204
    except Exception as e:
        logger.error(f"Failed to delete hike: {str(e)}")
        return jsonify({"error": str(e)}), 400




