import json
import logging

from databases import Database

from tables import xrates
import convertor_config

GET_RATE = "SELECT xrates.rate, xrates.valid FROM xrates WHERE xrates.from_curr=:v1 AND xrates.to_curr=:v2"
INVALIDATE_ALL_RATES = "UPDATE xrates SET valid=false"


logger = logging.getLogger("asyncio")
database = Database(convertor_config.DATABASE_URL)


def error_result(message):
    logger.info(message)
    return {'error': message}


async def connect_db():
    await database.connect()


async def disconnect_db():
    await database.disconnect()


async def database_post(method, params):
    status = 200
    if method == 'POST':
        try:
            merge = int(params['merge'])
        except (KeyError, ValueError):
            result = error_result('missing the query param: merge, or it has invalid value, allowed (0,1)')
            status = 400
        else:
            # transaction !!!!
            if not merge:  # invalidate all rates in the table
                await database.execute(query=INVALIDATE_ALL_RATES)
            result = {"result": "update done"}
    else:
        result = error_result(f'method {method} not allowed')
        status = 405

    return json.dumps(result), status


async def convert_get(method, params):
    status = 200
    if method == 'GET':
        try:
            from_curr = params['from']
            to_curr = params['to']
            from_amount = float(params['amount'])
        except (KeyError, ValueError):
            result = error_result('missing mandatory param(s) or invalid amount value')
            status = 400
        else:
            xrate = await database.fetch_one(query=GET_RATE, values={'v1': from_curr, 'v2': to_curr})
            if not xrate:
                result = error_result(f'unknown currency pair')
                status = 400
            elif not xrate['valid']:
                result = error_result(f'no valid rate for this currency pair')
                status = 400
            else:
                rate = xrate['rate']
                to_amount = from_amount * rate
                result = {'to_amount': f'{to_amount:.2f}'}
    else:
        result = error_result(f'method {method} not allowed')
        status = 405
    return json.dumps(result), status


routes = {  # simple routes (no url params)
    '/convert': convert_get,
    '/database': database_post
}
