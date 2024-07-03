# coding=utf-8
import pg8000
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector, IPTypes
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

    db_user = config.get('POSTGRES_USER')
    db_pass = config.get('POSTGRES_PASSWORD')
    db_name = config.get('POSTGRES_DB')
    instance_connection_name = config.get('INSTANCE_CONNECTION_NAME')

    ip_type = IPTypes.PRIVATE if config.get('PRIVATE_IP') else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    # only works with pg8000 driver
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


if env == "dev":  # dev
    Session = sessionmaker(bind=connect_without_connector(config=dotenv_values(f'./conf/dev.env')))
else:  # prod
    Session = sessionmaker(bind=connect_with_connector(config=dotenv_values(f'./conf/prod.env')))

session = Session()
Base = sqlalchemy.orm.declarative_base()
