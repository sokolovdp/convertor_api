import os
import logging

DEBUG_MODE = True
LOGGING_LEVEL = logging.DEBUG

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8888

MAX_REQUEST_LENGTH = 1024  # for sock_recv

DATABASE_URL = 'postgresql://postgres:postgres@localhost'
