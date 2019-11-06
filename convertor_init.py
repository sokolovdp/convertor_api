import asyncio
import socket
import json
import logging
from collections import namedtuple

Request = namedtuple('Request', 'method url params')


async def database_post(method, params):
    logger.debug(f'database view {method}')
    result = {'updated': 3}
    return json.dumps(result), 201


async def convert_get(method, params):
    logger.debug(f'converter view {method}')
    result = {'result': 3700.24}
    return json.dumps(result), 200


routes = {
    '/convert': convert_get,
    '/database': database_post
}


def make_header(status: int) -> bytes:
    msg = 'OK' if status in (200, 201) else 'ERROR'
    header = f'HTTP/1.1 {status} {msg}\r\nContent-Type: application/json\r\n\r\n'
    return header.encode()


def make_response(json_string, status=200) -> bytes:
    header = make_header(status)
    body = json_string.encode() if json_string else b''
    return header + body


def parse_query_string(query_str: str) -> dict:
    query_params = {}
    for param in query_str.split('&'):
        key, value = param.split('=')
        query_params[key] = value
    return query_params


def parse_request(request: bytes) -> tuple:
    query, *_, body = request.decode().split('\r\n')
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
        logger.debug(f'request: {request.method} {request.url}  {request.params}')
        if request.url in routes:
            body, status = await routes[request.url](request.method, request.params)
            logger.debug(f'response: {body} {status}')
        else:
            status = 404
            body = ''
        response = make_response(body, status)
        await main_loop.sock_sendall(conn, response)
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
