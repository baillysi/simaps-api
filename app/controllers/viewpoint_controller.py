from flask import Blueprint, jsonify, request
from app.services import viewpoint_service
from app.logger import logger

viewpoint_bp = Blueprint('viewpoint_bp', __name__, url_prefix='/api/viewpoints')


@viewpoint_bp.route('')
def get_viewpoints():
    filters = {}
    hike_id = request.args.get("hike_id")
    logger.info(f"GET request for viewpoints with hike {hike_id}")
    if hike_id:
        filters["hike_id"] = hike_id
    viewpoints = viewpoint_service.get_viewpoints(filters=filters)
    logger.info(f"{len(viewpoints)} viewpoints retrieved")
    return jsonify(viewpoints), 200




