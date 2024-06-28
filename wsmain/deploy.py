from flask import Flask,jsonify
from dataclasses import dataclass
from dotenv import load_dotenv

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

import os

app = Flask(__name__)


def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    """Initializes a Unix socket connection pool for a Cloud SQL instance of Postgres."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    load_dotenv(f"conf/deploy.env")
    db_user = os.environ["DB_USER"]  # e.g. 'my-database-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-database-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
    unix_socket_path = os.environ[
        "INSTANCE_UNIX_SOCKET"
    ]  # e.g. '/cloudsql/project:region:instance'

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>
        #                         ?unix_sock=<INSTANCE_UNIX_SOCKET>/.s.PGSQL.5432
        # Note: Some drivers require the `unix_sock` query parameter to use a different key.
        # For example, 'psycopg2' uses the path set to `host` in order to connect successfully.
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"},
        ),
        # ...
    )
    return pool


Session = sessionmaker(bind=connect_unix_socket())
Base = declarative_base()


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
    users = User.query.all()
    return jsonify(users), 200


if __name__ == "__main__":
    app.run(debug=True)

