# coding=utf-8
from flask import Flask, jsonify, request
from flask_cors import CORS
from model.data import Hike, Journey, Zone, Trail
from model.db import session
from sqlalchemy.orm import noload

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return 'Hello world'


@app.route('/zones/<int:zone_id>')
def get_zone(zone_id):
    zone = session.get(Zone, zone_id)
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


@app.route('/hikes', methods=['POST'])
def add_hike():
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

    session.add(new_hike)
    session.commit()
    return "", 201


@app.route('/hikes/<int:hike_id>', methods=['PUT'])
def update_hike(hike_id):
    hike = session.get(Hike, hike_id)
    hike.name = request.json['name']
    hike.distance = request.json['distance']
    hike.elevation = request.json['elevation']
    hike.difficulty = request.json['difficulty']
    hike.duration = request.json['duration']
    hike.journey_id = request.json['journey']['id']
    hike.rates = request.json['rates']
    hike.description = request.json['description']
    session.commit()
    return "", 200


@app.route('/hikes/<int:hike_id>', methods=['DELETE'])
def delete_hike(hike_id):
    hike = session.get(Hike, hike_id)
    session.delete(hike)
    session.commit()
    return "", 204


@app.route('/journeys')
def get_journeys():
    journeys = session.query(Journey).all()
    return jsonify(journeys), 200


@app.route('/trail')
def get_trail():
    hike_id = request.args.get('hike_id')
    trail = session.query(Trail).join(Hike, Hike.trail_id == Trail.id).filter(Hike.id == hike_id).one()
    return trail.__repr__(), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)

