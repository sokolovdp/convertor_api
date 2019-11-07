import json
import logging

logger = logging.getLogger("asyncio")


async def database_post(method, params):
    logger.debug(f'database view {method}')
    result = {'updated': 3}
    return json.dumps(result), 201


async def convert_get(method, params):
    logger.debug(f'converter view {method}')
    result = {'result': 3700.24}
    return json.dumps(result), 200


routes = {  # simple routes (no url params)
    '/convert': convert_get,
    '/database': database_post
}
