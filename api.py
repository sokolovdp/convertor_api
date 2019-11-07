from postgres_api import connect_db, disconnect_db, convert_get, database_post


routes = {  # simple routes (no url params)
    '/convert': convert_get,
    '/database': database_post
}
