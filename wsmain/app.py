# coding=utf-8
from flask import Flask, jsonify, request
from flask_cors import CORS
from model.data import Hike, Journey, Zone
from model.db import session
from sqlalchemy.orm import load_only

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return 'Hello world'


@app.route('/hikes')
def get_hikes():
    response = []
    if 'zone' in request.args:
        zone = request.args.get('zone')
        hikes = (session.query(Hike).join(Zone, Zone.id == Hike.zone_id).filter(Zone.name == zone)
                 .order_by(Hike.id).all())
    else:
        hikes = session.query(Hike).all()
    for h in hikes:
        response.append(h.__repr__())
    return jsonify(response), 200


@app.route('/hikes/<int:id_hike>')
def get_hike(id_hike):
    hike = session.get(Hike, id_hike)
    return hike.__repr__(), 200  # <class 'dict'>


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


@app.route('/hikes/<int:id_hike>', methods=['PUT'])
def update_hike(id_hike):
    hike = session.get(Hike, id_hike)
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


@app.route('/hikes/<int:id_hike>', methods=['DELETE'])
def delete_hike(id_hike):
    hike = session.get(Hike, id_hike)
    session.delete(hike)
    session.commit()
    return "", 204


@app.route('/zones/<int:id_zone>')
def get_zone(id_zone):
    zone = session.get(Zone, id_zone)  # <class 'model.zone.Zone'>
    return zone.__repr__(), 200  # <class 'dict'>


@app.route('/zones')
def get_zones():
    response = []
    fields = [Zone.name, Zone.id]
    zones = session.query(Zone).options(load_only(*fields))
    for z in zones:
        count = session.query(Hike).join(Zone, Zone.id == Hike.zone_id).filter(Zone.id == z.id).count()
        data = {
            'id': z.id,
            'name': z.name,
            'count': count
        }
        response.append(data)
    return jsonify(response), 200  # <class 'dict'>


@app.route('/zones/count')
def get_zones_hikes_count():
    response = {}
    for zone in range(1, session.query(Zone).count() + 1):
        count = session.query(Hike).join(Zone, Zone.id == Hike.zone_id).filter(Zone.id == zone).count()
        response[zone] = count
    return jsonify(response), 200  # <class 'dict'>


@app.route('/journeys')
def get_journeys():
    journeys = session.query(Journey).all()
    return jsonify(journeys), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)

