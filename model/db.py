# coding=utf-8
import pg8000
import sqlalchemy
import json
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import secretmanager
from dotenv import dotenv_values
from wsmain import env


def connect_without_connector(config):

    db_user = config.get('POSTGRES_USER')
    db_pass = config.get('POSTGRES_PASSWORD')
    db_name = config.get('POSTGRES_DB')

    pool = sqlalchemy.create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@localhost:5431/{db_name}")

    return pool


def connect_with_connector(config) -> sqlalchemy.engine.base.Engine:

    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # GCP project.
    project_id = config.get('project_id')

    # ID of the secret.
    secret_id = config.get('postgres_access_secret_id')

    # ID of the version
    version_id = config.get('postgres_access_version_id')

    # Build the resource name.
    name = client.secret_version_path(project_id, secret_id, version_id)

    # Get the secret version.
    response = client.access_secret_version(request={"name": name})

    # Get and use the payload.
    payload = json.loads(response.payload.data.decode("UTF-8"))

    db_user = payload['POSTGRES_USER']
    db_pass = payload['POSTGRES_PASSWORD']
    db_name = payload['POSTGRES_DB']

    instance_connection_name = payload['INSTANCE_CONNECTION_NAME']

    ip_type = IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    # only works with pg8000 driver
    connector = Connector(refresh_strategy="lazy")

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


if env == "dev":  # dev
    Session = sessionmaker(bind=connect_without_connector(config=dotenv_values(f'./conf/dev.env')))
else:  # prod
    Session = sessionmaker(bind=connect_with_connector(config=dotenv_values(f'./conf/prod.env')))

session = Session()
Base = sqlalchemy.orm.declarative_base()
