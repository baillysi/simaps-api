# coding=utf-8
import time

from flask import Flask, jsonify, request
from flask_cors import CORS
from model.data import Hike, Journey, Zone, Trail, Viewpoint, Region, Review
from model.db import Session
from sqlalchemy.orm import noload
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
def get_zone(zone_name):
    with Session() as session:
        zone = session.query(Zone).filter_by(name=zone_name).first()
        return zone.__repr__(), 200


@app.route('/regions/<zone_name>')
def get_regions_by_zone(zone_name):
    output = []
    with Session() as session:
        regions = (session.query(Region).join(Hike, Hike.region_id == Region.id).join(Zone, Zone.id == Hike.zone_id)
                   .filter(Zone.name == zone_name).filter(Hike.trail_id.isnot(None)).all())
        for hike in regions:
            output.append(hike.__repr__())
        return jsonify(output), 200


@app.route('/hikes/<int:hike_id>')
def get_hike(hike_id):
    with Session() as session:
        hike = session.get(Hike, hike_id)
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
        description=request.json['description'],
    )
    new_hike.journey_id = request.json['journey']['id']
    new_hike.region_id = request.json['region']['id']
    new_hike.zone_id = request.json['zone_id']

    with Session() as session:
        session.add(new_hike)
        session.commit()
        return '', 201


@app.route('/hikes/<int:hike_id>', methods=['PUT'])
def update_hike(hike_id):
    user = get_current_user()
    if not user:
        return '', 401

    with Session() as session:
        hike = session.get(Hike, hike_id)

        hike.name = request.json['name']
        hike.distance = request.json['distance']
        hike.elevation = request.json['elevation']
        hike.difficulty = request.json['difficulty']
        hike.duration = request.json['duration']
        hike.journey_id = request.json['journey']['id']
        hike.region_id = request.json['region']['id']
        hike.description = request.json['description']

        session.commit()
        return '', 200


@app.route('/hikes/<int:hike_id>', methods=['DELETE'])
def delete_hike(hike_id):
    user = get_current_user()
    if not user:
        return '', 401

    with Session() as session:
        hike = session.get(Hike, hike_id)
        session.delete(hike)
        session.commit()
        return '', 204


@app.route('/reviews')
def get_reviews():
    output = []
    with Session() as session:
        hike_id = request.args.get('hike_id')
        reviews = (session.query(Review).join(Hike, Hike.id == Review.hike_id).filter(Hike.id == hike_id)
                   .options(noload(Review.hike)).all())
        for review in reviews:
            output.append(review.__repr__())
        return jsonify(output), 200


@app.route('/reviews', methods=['POST'])
def add_review():
    user = get_current_user()
    if not user:
        return '', 401
    new_review = Review(
        title=request.json['title'],
        note=request.json['note'],
        rate=request.json['rate'],
    )
    new_review.hike_id = request.json['hike_id']
    new_review.is_validated = False

    with Session() as session:
        session.add(new_review)
        session.commit()
        return '', 201


@app.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    user = get_current_user()
    if not user:
        return '', 401

    with Session() as session:
        review = session.get(Review, review_id)
        review.is_validated = True
        session.commit()
        return '', 200


@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    user = get_current_user()
    if not user:
        return '', 401

    with Session() as session:
        review = session.get(Review, review_id)
        session.delete(review)
        session.commit()
        return '', 204


@app.route('/journeys')
def get_journeys():
    with Session() as session:
        journeys = session.query(Journey).all()
        return jsonify(journeys), 200


@app.route('/regions')
def get_regions():
    with Session() as session:
        regions = session.query(Region).all()
        return jsonify(regions), 200


@app.route('/trail')
def get_trail():
    with Session() as session:
        hike_id = request.args.get('hike_id')
        trail = session.query(Trail).join(Hike, Hike.trail_id == Trail.id).filter(Hike.id == hike_id).one()
        return trail.__repr__(), 200


@app.route('/viewpoints')
def get_viewpoints():
    output = []
    with Session() as session:
        hike_id = request.args.get('hike_id')
        if not hike_id:
            viewpoints = session.query(Viewpoint).all()
        else:
            viewpoints = (session.query(Viewpoint).join(Hike, Hike.id == Viewpoint.hike_id).filter(Hike.id == hike_id)
                          .options(noload(Viewpoint.hike)).all())

        for vp in viewpoints:
            output.append(vp.__repr__())
        return jsonify(output), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)
