import logging
from databases import Database
from sqlalchemy.exc import ArgumentError

import converter_config


GET_RATE = "SELECT xrates.rate, xrates.valid FROM xrates " \
           "WHERE xrates.from_curr=:from_curr AND xrates.to_curr=:to_curr"
INVALIDATE_ALL_RATES = "UPDATE xrates SET valid=false"
UPSERT_RATE = "INSERT INTO xrates (from_curr, to_curr, rate, valid) " \
              "VALUES (:from_curr, :to_curr, :rate, true) " \
              "ON CONFLICT (from_curr, to_curr) " \
              "DO UPDATE SET (rate, valid) = (:rate, true)"

logger = logging.getLogger("asyncio")
database = Database(converter_config.DATABASE_HOST)


async def connect_db():
    await database.connect()


async def disconnect_db():
    await database.disconnect()


def error_result(message: str) -> dict:
    logger.info(message)
    return {'error': message}


async def database_post(method: str, params: dict) -> tuple:
    if method not in ('POST', 'PUT', 'PATCH'):
        return error_result(f'method {method} not allowed'), 405

    try:
        merge = bool(params['merge'])
        rates = params['rates']
    except (KeyError, ValueError):
        return error_result('invalid params value(s), merge allowed value (0,1)'), 400

    transaction = await database.transaction()
    try:
        if not merge:  # invalidate all rates in the table
            await database.execute(query=INVALIDATE_ALL_RATES)
        await database.execute_many(query=UPSERT_RATE, values=rates)
    except (ArgumentError, KeyError):
        await transaction.rollback()
        return error_result('invalid rates data'), 400
    except Exception as e:
        await transaction.rollback()
        return error_result(f'database error: {repr(e)}'), 500
    else:
        await transaction.commit()

    return {'result': "rates updated"}, 200


async def convert_get(method: str, params: dict) -> tuple:
    if method != 'GET':
        return error_result(f'method {method} not allowed'), 405

    try:
        from_curr = params['from'].upper()
        to_curr = params['to'].upper()
        from_amount = float(params['amount'])
    except (KeyError, ValueError):
        return error_result('missing mandatory param(s) or invalid amount value'), 400

    value = await database.fetch_one(query=GET_RATE, values={'from_curr': from_curr, 'to_curr': to_curr})
    if not value:
        return error_result(f'unknown currency pair'), 400
    if not value['valid']:
        return error_result('no valid rate for this currency pair'), 400

    to_amount = from_amount * value['rate']
    return {'to_amount': f'{to_amount:.2f}'}, 200
