from sqlalchemy import create_engine
from orm_relations import *
from db_functions import *
from sqlalchemy.orm import sessionmaker
import xml.etree.ElementTree as ET


def init_db():
    engine = create_engine(
        'postgresql+psycopg2://postgres:passw0rd@db/stock')
    Base.metadata.drop_all(engine)  # drop all created tables
    print("drop all tables")
    # create all tables according to the metadata defined in orm_relations.
    Base.metadata.create_all(engine)


def connect_db():
    engine = create_engine(
        'postgresql+psycopg2://postgres:passw0rd@db/stock')
    return engine
