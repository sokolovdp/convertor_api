import logging
import convertor_config

import asyncio_redis

logger = logging.getLogger("asyncio")
redis_connection = None


async def connect_db():
    global redis_connection

    redis_connection = await asyncio_redis.Pool.create(
        host=convertor_config.DATABASE_HOST,
        port=convertor_config.DATABASE_PORT,
        poolsize=convertor_config.REDIS_POOL_SIZE
    )


async def disconnect_db():
    global redis_connection

    await redis_connection.close()


def error_result(message):
    logger.info(message)
    return {'error': message}


async def database_post(method, params):
    if method not in ('POST', 'PUT', 'PATCH'):
        result = error_result(f'method {method} not allowed')
        return result, 405

    try:
        merge = bool(params['merge'])
        rates = params['rates']
    except (KeyError, ValueError):
        result = error_result('missing the query param: merge, or it has invalid value, allowed (0,1)')
        return result, 400

    transaction = await redis_connection.multi()
    try:
        # Run commands in transaction (they return future objects)
        # f1 = await transaction.set('key', 'value')
        # f2 = await transaction.set('another_key', 'another_value')
        raise ZeroDivisionError
        pass
    except Exception as e:
        await transaction.rollback()
        result = error_result(f'redis error: {repr(e)}')
        status = 500
    else:
        # Commit transaction
        await transaction.exec()
        result = {'result': "rates updated"}
        status = 200

    return result, status


async def convert_get(method, params):
    return