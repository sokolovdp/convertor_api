from sqlalchemy import MetaData, Table, Column, FLOAT, Boolean, CHAR

metadata = MetaData()

xrates = Table(
    'xrates', metadata,
    Column('from_curr', CHAR(3), nullable=False),
    Column('to_curr', CHAR(3), nullable=False),
    Column('rate', FLOAT, nullable=False),
    Column('valid', Boolean, nullable=False),
)
