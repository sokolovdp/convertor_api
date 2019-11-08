import converter_config

if converter_config.DATABASE_TYPE == 'redis':
    from redis_api import connect_db, disconnect_db, convert_get, database_post
else:
    from postgres_api import connect_db, disconnect_db, convert_get, database_post


routes = {  # simple routes (no url params)
    '/convert': convert_get,
    '/database': database_post
}
