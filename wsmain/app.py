# This is a sample Python script.

from flask import Flask, jsonify, request
from model.host import Host
from model.hike import Hike
from model.base import Session

session = Session()

app = Flask(__name__)


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
    hikes = session.query(Hike).all()
    return jsonify(hikes), 200


@app.route('/hikes', methods=['POST'])
def add_hike():
    new_hike = Hike(
        name=request.json['name'],
        distance=request.json['distance']
    )
    for host_id in request.json['hosts']:
        print(host_id)
        host = session.query(Host).get(host_id)
        new_hike.hosts.append(host)

    session.add(new_hike)
    session.commit()
    return "", 201


@app.route('/hikes/<int:id_hike>', methods=['DELETE'])
def delete_hike(id_hike):
    hike = session.get(Hike, id_hike)
    session.delete(hike)
    session.commit()
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5001)
