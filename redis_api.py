import logging
import convertor_config
import json
import asyncio_redis

logger = logging.getLogger("asyncio")
redis_connection = None


async def connect_db():
    global redis_connection

    redis_connection = await asyncio_redis.Connection.create(  # for production better to use Pool
        host=convertor_config.DATABASE_HOST,
        port=convertor_config.DATABASE_PORT,
        # db=convertor_config.DATABASE_NAME
    )


async def disconnect_db():
    global redis_connection

    redis_connection.close()


def error_result(message):
    logger.info(message)
    return {'error': message}


async def get_all_keys():
    keys = await redis_connection.keys('??????')
    all_keys = set()
    for key in keys:
        k = await key
        all_keys.add(k)
    return all_keys


async def database_post(method, params):
    if method not in ('POST', 'PUT', 'PATCH'):
        result = error_result(f'method {method} not allowed')
        return result, 405

    try:
        merge = int(params['merge'])
        rates = params['rates']
    except (KeyError, ValueError):
        result = error_result('missing the query param: merge, or it has invalid value, allowed (0,1)')
        return result, 400

    keys_in_db = await get_all_keys()
    new_rates = dict()
    new_keys = set()
    for rate in rates:
        key = rate['from_curr'][:3].upper() + rate['to_curr'][:3].upper()
        value = {'valid': 1, 'rate': float(rate['rate'])}
        new_rates[key] = json.dumps(value)
        new_keys.add(key)

    if not merge:  # invalidate all rates
        keys_to_invalidate = keys_in_db - new_keys
        pass


    transaction = await redis_connection.multi()
    try:
        for key, value in new_rates.items():
            await transaction.set(key, value)
    except Exception as e:
        result = error_result(f'redis error: {repr(e)}')
        status = 500
    else:
        # Commit transaction
        await transaction.exec()
        result = {'result': "rates updated"}
        status = 200

    return result, status


async def convert_get(method, params):
    if method != 'GET':
        result = error_result(f'method {method} not allowed')
        return result, 405

    try:
        from_curr = params['from'][:3].upper()
        to_curr = params['to'][:3].upper()
        from_amount = float(params['amount'])
    except (KeyError, ValueError):
        result = error_result('missing mandatory param(s) or invalid amount value')
        return result, 400

    key = from_curr + to_curr
    json_string = await redis_connection.get(key)
    if not json_string:
        result = error_result(f'unknown currency pair')
        return result, 400
    value = json.loads(json_string)
    rate = value.get('rate')
    valid = value.get('valid')
    if not valid:
        result = error_result(f'no valid rate for this currency pair')
        status = 400
    else:
        to_amount = from_amount * rate
        result = {'to_amount': f'{to_amount:.2f}'}
        status = 200

    return result, status
