import json
from collections import namedtuple
import asyncio
import socket
import logging

import api
import converter_config

Request = namedtuple('Request', 'method url params')

logging.basicConfig(
    level=converter_config.LOGGING_LEVEL,
    format=converter_config.LOGGING_FORMAT,
    datefmt=converter_config.LOGGING_DATE_FORMAT
)
logger = logging.getLogger("asyncio")


def make_header(status: int) -> bytes:
    msg = 'OK' if status in (200, 201) else 'ERROR'
    header = f'HTTP/1.1 {status} {msg}\r\nContent-Type: application/json\r\n\r\n'
    return header.encode()


def make_response(result: dict, status: int) -> bytes:
    json_string = json.dumps(result)
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
        body_params = json.loads(body)  # request body must be a dict, else error!
        params.update(body_params)
    return method, url, params


async def request_handler(main_loop, conn):
    req_bytes = await main_loop.sock_recv(conn, converter_config.MAX_REQUEST_LENGTH)
    if req_bytes:
        try:
            request = Request(*parse_request(req_bytes))
            logger.debug(f'request: {request.method} {request.url}  {request.params}')
            result, status = await api.routes[request.url](request.method, request.params)
        except KeyError:
            result, status = {"error": "unknown api route url"}, 404
        except (ValueError, TypeError):
            result, status = {"error": "invalid request params"}, 400
        except Exception as e:
            result, status = {"error": f"server error: {str(e)}"}, 500
        response = make_response(result, status)
        await main_loop.sock_sendall(conn, response)
    conn.close()


async def http_server(sock, main_loop):
    logger.info('converter server started...')
    while True:
        conn, addr = await main_loop.sock_accept(sock)
        main_loop.create_task(request_handler(main_loop, conn))


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(False)
    server_socket.bind((converter_config.SERVER_HOST, converter_config.SERVER_PORT))
    server_socket.listen(10)

    main_loop = asyncio.get_event_loop()
    main_loop.set_debug(enabled=converter_config.DEBUG_MODE)

    try:
        main_loop.run_until_complete(api.connect_db())
        main_loop.run_until_complete(http_server(server_socket, main_loop))
    except KeyboardInterrupt:
        pass
    finally:
        main_loop.run_until_complete(api.disconnect_db())
        main_loop.close()
        server_socket.close()


if __name__ == "__main__":
    main()
