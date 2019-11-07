import json
from collections import namedtuple
import asyncio
import socket
import logging

import api
import convertor_config

Request = namedtuple('Request', 'method url params')

logging.basicConfig(
    level=convertor_config.LOGGING_LEVEL,
    format=convertor_config.LOGGING_FORMAT,
    datefmt=convertor_config.LOGGING_DATE_FORMAT
)
logger = logging.getLogger("asyncio")


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
    for param in query_str.split('&'):  # expected params with unique names!
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
        body_params = json.loads(body)  # must be a dict, else error!
        params.update(body_params)
    return method, url, params


async def request_handler(main_loop, conn):
    req_bytes = await main_loop.sock_recv(conn, convertor_config.MAX_REQUEST_LENGTH)
    if req_bytes:
        try:
            request = Request(*parse_request(req_bytes))
            logger.debug(f'request: {request.method} {request.url}  {request.params}')
            body, status = await api.routes[request.url](request.method, request.params)
            logger.debug(f'response: {body} {status}')
        except KeyError:
            status = 404
            body = '{"error": "unknown api path"}'
        except (ValueError, TypeError):
            status = 400
            body = '{"error": "invalid request params"}'
        response = make_response(body, status)
        await main_loop.sock_sendall(conn, response)
    conn.close()


async def http_server(sock, loop):
    await api.connect_db()
    logger.debug('converter server started.....')
    while True:
        conn, addr = await loop.sock_accept(sock)
        loop.create_task(request_handler(loop, conn))


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(False)
    server_socket.bind((convertor_config.SERVER_HOST, convertor_config.SERVER_PORT))
    server_socket.listen(10)

    main_loop = asyncio.get_event_loop()
    main_loop.set_debug(enabled=convertor_config.DEBUG_MODE)

    try:
        main_loop.run_until_complete(http_server(server_socket, main_loop))
    except KeyboardInterrupt:
        pass
    finally:
        main_loop.close()
        server_socket.close()


if __name__ == "__main__":
    main()
