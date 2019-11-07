import json
import logging

import tables

logger = logging.getLogger("asyncio")


def start_api():
    tables.connect_database()


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

            result = {'converted': 3}
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
