import asyncio
import socket
import json
import logging
from collections import namedtuple

Request = namedtuple('Request', 'method url params')


def database_post(method, params):
    return None


def convert_get(method, params):
    return None


routes = {
    '/converter': convert_get,
    '/database': database_post
}


def make_header_ok():
    header = b"HTTP/1.1 200 OK\r\n"
    header += b"Content-Type: application/json\r\n"
    header += b"\r\n"
    return header


def make_header_err():
    header = b"HTTP/1.1 400 ERROR\r\n"
    header += b"Content-Type: application/json\r\n"
    header += b"\r\n"
    return header


def make_body_ok():
    resp = b'{'
    resp += b'"data": "hello world"'
    resp += b'}'
    return resp


def make_body_err():
    resp = b'{'
    resp += b'"error": "invalid params"'
    resp += b'}'
    return resp


def parse_query_string(query_str: str) -> dict:
    query_params = {}
    for param in query_str.split('&'):
        key, value = param.split('=')
        query_params[key] = value
    return query_params


def parse_request(request: bytes) -> tuple:
    query, *_, body = request.decode('utf-8').split('\r\n')
    method, url, *_ = query.split(' ')
    params = {}
    if '?' in url:
        url, query_params = url.split('?', 1)
        params.update(parse_query_string(query_params))
    if body:
        body_params = json.loads(body)
        params.update(body_params)
    return method, url, params


host = 'localhost'
port = 8888
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.setblocking(False)
server_socket.bind((host, port))
server_socket.listen(10)

main_loop = asyncio.get_event_loop()
main_loop.set_debug(enabled=True)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("asyncio")


async def request_handler(conn):
    req_bytes = await main_loop.sock_recv(conn, 1024)
    if req_bytes:
        request = Request(*parse_request(req_bytes))
        logger.info(f'{request.method} {request.url}  {request.params}')
        resp = make_header_err()
        resp += make_body_err()
        await main_loop.sock_sendall(conn, resp)
    conn.close()


async def http_server(sock, loop):
    logger.debug('converter server started.....')
    while True:
        conn, addr = await loop.sock_accept(sock)
        loop.create_task(request_handler(conn))


try:
    main_loop.run_until_complete(http_server(server_socket, main_loop))
except KeyboardInterrupt:
    pass
finally:
    main_loop.close()
    server_socket.close()
