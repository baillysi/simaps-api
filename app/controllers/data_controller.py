from flask import Blueprint, jsonify
from app.services import data_service
from app.logger import logger

region_bp = Blueprint('region_bp', __name__, url_prefix='/api/regions')
journey_bp = Blueprint('journey_bp', __name__, url_prefix='/api/journeys')
zone_bp = Blueprint('zone_bp', __name__, url_prefix='/api/zones')


@zone_bp.route('/<int:zone_id>')
def get_zone(zone_id):
    logger.info(f"GET request for zone with ID {zone_id}")
    zone = data_service.get_zone_by_id(zone_id)
    if not zone:
        logger.warning(f"Zone with ID {zone_id} not found")
        return jsonify({'error': 'Zone not found'}), 404
    logger.info(f"Zone with ID {zone_id} found")
    return zone, 200


@region_bp.route('')
def get_regions():
    logger.info(f"GET request for regions")
    regions = data_service.get_regions()
    return jsonify(regions), 200


@journey_bp.route('')
def get_journeys():
    logger.info(f"GET request for journeys")
    journeys = data_service.get_journeys()
    return jsonify(journeys), 200





