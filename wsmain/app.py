# coding=utf-8
from flask import Flask, jsonify, request
from flask_cors import CORS
from model.data import Hike, Journey, Zone, Trail, Viewpoint
from model.db import session
from sqlalchemy.orm import noload
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, SQLAlchemyError
import json

from firebase_admin import initialize_app, credentials
from firebase_admin.auth import verify_id_token

from google.cloud import secretmanager
from dotenv import dotenv_values

from wsmain import env

# firebase app
if env == "dev":  # dev
    _FIREBASE_APP = initialize_app()
else:  # prod
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    config = dotenv_values(f'./conf/prod.env')

    # GCP project.
    project_id = config.get('project_id')

    # ID of the secret.
    secret_id = config.get('firebase_sdk_admin_secret_id')

    # ID of the version
    version_id = config.get('firebase_sdk_admin_version_id')

    # Build the resource name.
    name = client.secret_version_path(project_id, secret_id, version_id)

    # Get the secret version.
    response = client.access_secret_version(request={"name": name})

    # Get and use the payload.
    payload = json.loads(response.payload.data.decode("UTF-8"))

    creds = credentials.Certificate(payload)

    _FIREBASE_APP = initialize_app(credential=creds)


# flask app
app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return 'Hello world'


@app.route("/user")
def get_current_user():
    # Return None if no Authorization header.
    if "Authorization" not in request.headers:
        return None
    authorization = request.headers["Authorization"]

    # Authorization header format is "Bearer <token>".
    # This matches OAuth 2.0 spec:
    # https://www.rfc-editor.org/rfc/rfc6750.txt.
    if not authorization.startswith("Bearer "):
        return None

    token = authorization.split("Bearer ")[1]

    # Verify that the token is valid.
    result = verify_id_token(token)
    # Return the user ID of the authenticated user.
    return result["uid"]


@app.route('/zones/<zone_name>')
def get_zone_by_name(zone_name):
    zone = session.query(Zone).filter_by(name=zone_name).first()
    return zone.__repr__(), 200


@app.route('/zones/count')
def get_zones_hikes_count():
    response = {}
    for zone in range(1, session.query(Zone).count() + 1):
        count = session.query(Hike).join(Zone, Zone.id == Hike.zone_id).filter(Zone.id == zone).count()
        response[zone] = count
    return jsonify(response), 200


@app.route('/hikes/<int:hike_id>')
def get_hike(hike_id):
    hike = session.get(Hike, hike_id, options=[noload(Hike.trail)])
    return hike.__repr__(), 200


@app.route('/hikes/latest')
def get_latest_hike():
    hike = session.query(Hike).order_by(Hike.id.desc()).first()
    return hike.__repr__(), 200


@app.route('/hikes', methods=['POST'])
def add_hike():
    user = get_current_user()
    if not user:
        return '', 401
    new_hike = Hike(
        name=request.json['name'],
        distance=request.json['distance'],
        elevation=request.json['elevation'],
        difficulty=request.json['difficulty'],
        duration=request.json['duration'],
        rates=request.json['rates'],
        description=request.json['description'],
    )
    new_hike.journey_id = request.json['journey']['id']
    new_hike.zone_id = request.json['zone_id']

    try:
        session.add(new_hike)
    except SQLAlchemyError as err:
        session.rollback()
        raise err
    else:
        session.commit()
        return '', 201


@app.route('/hikes/<int:hike_id>', methods=['PUT'])
def update_hike(hike_id):
    user = get_current_user()
    if not user:
        return '', 401
    hike = session.get(Hike, hike_id)

    try:
        hike.name = request.json['name']
        hike.distance = request.json['distance']
        hike.elevation = request.json['elevation']
        hike.difficulty = request.json['difficulty']
        hike.duration = request.json['duration']
        hike.journey_id = request.json['journey']['id']
        hike.rates = request.json['rates']
        hike.description = request.json['description']
    except SQLAlchemyError as err:
        session.rollback()
        raise err
    else:
        session.commit()
        return '', 200


@app.route('/hikes/<int:hike_id>', methods=['DELETE'])
def delete_hike(hike_id):
    user = get_current_user()
    if not user:
        return '', 401
    hike = session.get(Hike, hike_id)

    try:
        session.delete(hike)
    except SQLAlchemyError as err:
        session.rollback()
        raise err
    else:
        session.commit()
        return '', 204


@app.route('/journeys')
def get_journeys():
    journeys = session.query(Journey).all()
    return jsonify(journeys), 200


@app.route('/trail')
def get_trail():
    hike_id = request.args.get('hike_id')
    trail = session.query(Trail).join(Hike, Hike.trail_id == Trail.id).filter(Hike.id == hike_id).one()
    return trail.__repr__(), 200


@app.route('/viewpoints/<int:vp_id>')
def get_viewpoint(vp_id):
    viewpoint = session.get(Viewpoint, vp_id)
    return viewpoint.__repr__(), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)
