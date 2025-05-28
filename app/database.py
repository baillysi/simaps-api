import json
import sqlalchemy
from sqlalchemy import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from google.cloud import secretmanager
from app.config import env, config
from app.logger import logger


def connect_without_connector():
    db_user = config.get('POSTGRES_USER')
    db_pass = config.get('POSTGRES_PASSWORD')
    db_name = config.get('POSTGRES_DB')
    try:
        logger.info(f"Attempting to connect to local database '{db_name}' as user '{db_user}'")
        local_engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@localhost:5431/{db_name}")
        logger.info("Successfully connected to local database.")
        return local_engine
    except OperationalError as err:
        logger.error("Failed to connect to local database.")
        raise err


def connect_unix_socket():
    try:
        logger.info("Attempting to connect to Cloud SQL via Unix socket.")
        client = secretmanager.SecretManagerServiceClient()
        name = client.secret_version_path(config['project_id'], config['postgres_access_secret_id'],
                                          config['postgres_access_version_id'])
        payload = json.loads(client.access_secret_version(request={"name": name}).payload.data.decode("UTF-8"))

        cloudsql_engine = sqlalchemy.create_engine(
            URL.create(
                drivername="postgresql+psycopg2",
                username=payload['POSTGRES_USER'],
                password=payload['POSTGRES_PASSWORD'],
                database=payload['POSTGRES_DB'],
                host=f"/cloudsql/{payload['INSTANCE_CONNECTION_NAME']}",
            ),
            pool_pre_ping=True,
            connect_args={
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            }
        )
        logger.info("Successfully connected to Cloud SQL.")
        return cloudsql_engine
    except OperationalError as err:
        logger.error("Failed to connect to Cloud SQL.")
        raise err


engine = connect_without_connector() if env == "dev" else connect_unix_socket()
Session = sessionmaker(bind=engine)
Base = sqlalchemy.orm.declarative_base()
