from flask import Flask,jsonify
from dataclasses import dataclass
from dotenv import load_dotenv

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

from google.cloud.sql.connector import Connector, IPTypes
import pg8000

import os

app = Flask(__name__)


def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    load_dotenv(f"conf/deploy.env")

    instance_connection_name = os.environ[
        "INSTANCE_CONNECTION_NAME"
    ]  # e.g. 'project:region:instance'
    db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # ...
    )
    return pool


Session = sessionmaker(bind=connect_with_connector())
session = Session()
Base = sqlalchemy.orm.declarative_base()


@dataclass
class User(Base):
    __tablename__ = 'users'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    zone: str = Column(String)

    def __repr__(self):
        return {
            "id": self.id,
            "name": self.name,
            "zone": self.zone
        }


@app.route("/")
def hello_world():
    return 'Hello world'


@app.route('/users')
def get_users():
    users = session.query(User).all()
    return jsonify(users), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)

