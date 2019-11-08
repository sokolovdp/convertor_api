import os
import logging

# asyncio settings:
DEBUG_MODE = True
LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = "%(asctime)s,%(msecs)d %(levelname)s: %(message)s"
LOGGING_DATE_FORMAT = "%H:%M:%S"
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8888
MAX_REQUEST_LENGTH = 1024  # for sock_recv

# database settings:
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'redis')

if DATABASE_TYPE == 'redis':
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', 6379)
else:
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'postgresql://postgres:postgres@localhost')

