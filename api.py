import json
import logging

from databases import Database

from tables import xrates
import convertor_config

logger = logging.getLogger("asyncio")
database = Database(convertor_config.DATABASE_URL)


async def connect_db():
    await database.connect()


async def database_post(method, params):
    logger.debug(f'converter view {method}')
    result = {'result': 3700.24}
    return json.dumps(result), 200


async def convert_get(method, params):
    status = 200
    if method == 'GET':
        logger.debug(f'database view {method}')
        from_curr = params.get('from')
        to_curr = params.get('to')
        from_amount = params.get('amount')
        if not all([from_amount, from_curr, to_curr]):
            error = 'missing mandatory query param(s)'
            logger.info(error)
            result = {'error': error}
            status = 400
        else:
            query = xrates.select().where(xrates.c.from_curr == from_curr).where(xrates.c.to_curr == to_curr)
            xrate = await database.fetch_one(query)
            result = {'type': str(type(xrate))}
    else:
        error = f'invalid method {method}'
        logger.info(error)
        result = {'error': error}
        status = 405
    return json.dumps(result), status


routes = {  # simple routes (no url params)
    '/convert': convert_get,
    '/database': database_post
}
