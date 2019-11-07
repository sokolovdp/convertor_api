import logging
import convertor_config

import asyncio_redis

logger = logging.getLogger("asyncio")
connection = None


async def connect_db():
    global connection

    connection = await asyncio_redis.Pool.create(
        host=convertor_config.DATABASE_HOST,
        port=convertor_config.DATABASE_PORT,
        poolsize=convertor_config.REDIS_POOL_SIZE
    )


async def disconnect_db():
    global connection

    await connection.close()
