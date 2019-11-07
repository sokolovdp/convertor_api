import os

from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError

import tables

initial_xrates = [
    {
        'from_currency': 'USD',
        'to_currency': 'RUB',
        'rate': 63.70,
        'valid': True
    },
    {
        'from_currency': 'RUB',
        'to_currency': 'USD',
        'rate': 0.016,
        'valid': True

    },
    {
        'from_currency': 'EUR',
        'to_currency': 'RUB',
        'rate': 70.54,
        'valid': True
    },
    {
        'from_currency': 'RUB',
        'to_currency': 'EUR',
        'rate': 0.014,
        'valid': True

    }
]

if __name__ == '__main__':
    database_url = tables.DATABASE_URL

    print(f'creating xrates tables, database url="{database_url}" ...')

    db_engine = create_engine(database_url, echo=True)
    db_connection = db_engine.connect()
    try:
        tables.xrates.create(db_connection)
        # create unique multicolumn index
        db_connection.execute('CREATE UNIQUE INDEX from_to_idx ON xrates (from_currency, to_currency)')
    except DBAPIError as db_error:
        print(f'\nDB error code: {db_error.orig.pgcode}\n')

    query = tables.xrates.insert()
    db_connection.execute(query, initial_xrates)

    print('\nxrate table created and populated with initial data\n')
