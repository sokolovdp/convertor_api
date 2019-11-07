import os

from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError
from psycopg2.errorcodes import DUPLICATE_TABLE

import tables


if __name__ == '__main__':
    database_url = tables.DATABASE_URL

    print(f'creating xrates tables, database url="{database_url}" ...')

    db_engine = create_engine(database_url, echo=True)
    db_connection = db_engine.connect()
    try:
        tables.xrates.create(db_connection)
    except DBAPIError as db_error:
        if db_error.orig.pgcode == DUPLICATE_TABLE:
            print('\nxrate table already exists!\n')
            pass
        else:
            raise db_error

    # create multicolumn index
    db_connection.execute('CREATE INDEX from_to_idx ON xrates (from_currency, to_currency)')

    # query = tables.xrates.insert()
    # db_connection.execute(query, )

    print('\nxrate table created and populated with initial data\n')
