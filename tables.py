from sqlalchemy import MetaData, Table, Column, FLOAT, Boolean, CHAR
from databases import Database
from convertor_config import DATABASE_URL

metadata = MetaData()

xrates = Table(
    'xrates', metadata,
    Column('from_curr', CHAR(3),  nullable=False),
    Column('to_curr', CHAR(3), nullable=False),
    Column('rate', FLOAT,  nullable=False),
    Column('valid', Boolean, nullable=False),
)


def connect_database():
    db = Database(DATABASE_URL)
    db.connect()
    return db
