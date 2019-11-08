import logging
import json
import asyncio_redis
from collections import namedtuple

import convertor_config

logger = logging.getLogger("asyncio")
redis_connection = None
Value = namedtuple('Value', 'rate valid')  # tuple to store rate and valid flag


async def connect_db():
    global redis_connection

    redis_connection = await asyncio_redis.Connection.create(  # for production use Pool, and create DB
        host=convertor_config.DATABASE_HOST,
        port=convertor_config.DATABASE_PORT,
    )


async def disconnect_db():
    global redis_connection

    redis_connection.close()


def error_result(message):
    logger.info(message)
    return {'error': message}


async def get_db_keys() -> set:
    cursor = await redis_connection.scan('??????')
    keys = await cursor.fetchall()
    return keys


async def run_update_transaction(data: dict):
    transaction = await redis_connection.multi()
    try:
        for key, value in data.items():
            await transaction.set(key, value)
    except Exception:
        raise
    else:  # Commit transaction
        await transaction.exec()


async def database_post(method, params):
    if method not in ('POST', 'PUT', 'PATCH'):
        return error_result(f'method {method} not allowed'), 405

    try:
        merge = int(params['merge'])
        rates = params['rates']
    except (KeyError, ValueError):
        return error_result('invalid params value(s), merge allowed value (0,1)'), 400

    new_rates = dict()
    for rate in rates:
        key = rate['from_curr'][:3].upper() + rate['to_curr'][:3].upper()
        new_rates[key] = json.dumps(Value(rate=float(rate['rate']), valid=1))

    if not merge:  # invalidate rates in db, which are not present in update request
        db_keys = await get_db_keys()
        keys_to_invalidate = set(db_keys) - set(new_rates.keys())
        invalid_rates = dict()
        for key in keys_to_invalidate:
            json_string = await redis_connection.get(key)
            old_value = Value(*json.loads(json_string))
            invalid_rates[key] = json.dumps(Value(rate=old_value.rate, valid=0))
        try:
            await run_update_transaction(invalid_rates)
        except Exception as e:
            return error_result(f'redis error: {repr(e)}'), 500

    try:  # update db with new rates
        await run_update_transaction(new_rates)
    except Exception as e:
        return error_result(f'redis error: {repr(e)}'), 500

    return {'result': "rates updated"}, 200


async def convert_get(method, params):
    if method != 'GET':
        return error_result(f'method {method} not allowed'), 405

    try:
        from_curr = params['from'][:3].upper()
        to_curr = params['to'][:3].upper()
        from_amount = float(params['amount'])
    except (KeyError, ValueError):
        return error_result('missing mandatory param(s) or invalid amount value'), 400

    key = from_curr + to_curr
    json_string = await redis_connection.get(key)
    if not json_string:
        return error_result(f'unknown currency pair'), 400
    value = Value(*json.loads(json_string))
    if not value.valid:
        return error_result(f'no valid rate for this currency pair'), 400

    to_amount = from_amount * value.rate
    return {'to_amount': f'{to_amount:.2f}'}, 200
