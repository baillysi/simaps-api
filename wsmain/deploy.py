# coding=utf-8
from flask import Flask, jsonify
from model.hike import Hike
from model.db import session

app = Flask(__name__)


@app.route("/")
def hello_world():
    return 'Hello world'


@app.route('/hikes')
def get_hikes():
    hikes = session.query(Hike).all()
    return jsonify(hikes), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)

