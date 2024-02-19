# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Table, ForeignKey
from dotenv import dotenv_values

config = dotenv_values("/home/simon/PycharmProjects/simaps-api/conf/dev.env")

host = config.get('DB_HOST')
user = config.get('DB_USER')
password = config.get('DB_PASSWORD')
database = config.get('DB_DATABASE')
port = config.get('DB_PORT')
schema = config.get('DB_SCHEMA')

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
                       f"?options=-c%20search_path={schema}")
Session = sessionmaker(bind=engine)

Base = declarative_base()

hosts_hikes_association = Table(
    'hosts_hikes', Base.metadata,
    Column('host_id', Integer, ForeignKey('hosts.id')),
    Column('hike_id', Integer, ForeignKey('hikes.id'))
)
