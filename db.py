from sqlalchemy import MetaData, Table, Column, FLOAT, Boolean, CHAR
from databases import Database
import convertor_config

metadata = MetaData()

xrates = Table(
    'xrates', metadata,
    Column('from', CHAR(3),  nullable=False),
    Column('to', CHAR(3), nullable=False),
    Column('rate', FLOAT,  nullable=False),
    Column('valid', Boolean, nullable=False),
)


def connect_database():
    db = Database(convertor_config.DATABASE_URL)
    db.connect()
    return db
