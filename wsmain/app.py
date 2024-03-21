# This is a sample Python script.
import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from model.host import Host
from model.hike import Hike
from model.zone import Zone
from model.base import Session

session = Session()

app = Flask(__name__)
CORS(app)


@app.route('/hosts')
def get_hosts():
    hosts = session.query(Host).all()
    return jsonify(hosts), 200


@app.route('/hosts/<int:id_host>')
def get_host(id_host):
    host = session.get(Host, id_host)  # Returns the row referenced by the primary key parameter passed as argument.
    return host.__repr__(), 200


@app.route('/hosts', methods=['POST'])
def add_host():
    new_host = Host(
        name=request.json['name'],
        zone=request.json['zone'],
        price=request.json['price']
    )
    session.add(new_host)
    session.commit()
    return "", 201


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
    return json.dumps(response), 200


@app.route('/hikes/<int:id_hike>')
def get_hike(id_hike):
    hike = session.get(Hike, id_hike)
    return hike.__repr__(), 200  # <class 'dict'>


@app.route('/hikes', methods=['POST'])
def add_hike():
    new_hike = Hike(
        name=request.json['name'],
        distance=request.json['distance'],
        # gpx=request.json['gpx']
    )
    new_hike.zone_id = request.json['zone_id']
    for host_id in request.json['hosts']:
        host = session.query(Host).get(host_id)
        new_hike.hosts.append(host)

    session.add(new_hike)
    session.commit()
    return "", 201


@app.route('/hikes/<int:id_hike>', methods=['PUT'])
def update_hike(id_hike):
    hike = session.get(Hike, id_hike)
    hike.name = request.json['name']
    hike.distance = request.json['distance']
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


if __name__ == "__main__":
    app.run(debug=True, port=5001)
