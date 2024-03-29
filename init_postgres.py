from sqlalchemy import create_engine, MetaData, Table, Column, FLOAT, Boolean, CHAR
from sqlalchemy.exc import DBAPIError, IntegrityError

import converter_config


xrates = Table(
    'xrates', MetaData(),
    Column('from_curr', CHAR(3), nullable=False),
    Column('to_curr', CHAR(3), nullable=False),
    Column('rate', FLOAT, nullable=False),
    Column('valid', Boolean, nullable=False),
)


initial_xrates = [
    {
        "from_curr": "USD",
        "to_curr": "RUB",
        "rate": 63.70,
        "valid": True
    },
    {
        "from_curr": "RUB",
        "to_curr": "USD",
        "rate": 0.016,
        "valid": True
    },
    {
        "from_curr": "EUR",
        "to_curr": "RUB",
        "rate": 70.54,
        "valid": True
    },
    {
        "from_curr": "RUB",
        "to_curr": "EUR",
        "rate": 0.014,
        "valid": True
    }
]

if __name__ == '__main__':
    database_url = converter_config.DATABASE_HOST

    print(f'creating xrates tables, database url="{database_url}" ...')

    db_engine = create_engine(database_url, echo=True)
    db_connection = db_engine.connect()
    try:
        xrates.create(db_connection)
        # create unique multicolumn index
        db_connection.execute('CREATE UNIQUE INDEX from_to_idx ON xrates (from_curr, to_curr)')
    except DBAPIError as db_error:
        if db_error.orig.pgcode == '42P07':
            print('\nxrates table already exists!\n')
        else:
            print(f'\nDB error code: {db_error.orig.pgcode}\n')

    try:
        query = xrates.insert()
        db_connection.execute(query, initial_xrates)
    except IntegrityError:
        print('\nxrates data already filled in!\n')

    print('\nxrate table created and populated with initial data\n')
