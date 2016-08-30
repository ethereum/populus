import random
import gevent
import contextlib

try:
    from http.server import (
        HTTPServer,
        BaseHTTPRequestHandler,
    )
except ImportError:
    from BaseHTTPServer import (
        HTTPServer,
        BaseHTTPRequestHandler,
    )

from populus.utils.networking import (
    get_open_port,
    wait_for_connection,
)


def test_wait_for_connection_success():
    success_tracker = {}
    port = get_open_port()

    def _do_client():
        try:
            wait_for_connection('localhost', port)
        except gevent.Timeout:
            success_tracker['client_success'] = False
        else:
            success_tracker['client_success'] = True


    class TestHTTPServer(HTTPServer):
        timeout = 30

        def handle_timeout():
            success_tracker['server_success'] = False

        def handle_error():
            success_tracker['server_success'] = True

    def _do_server():
        server = TestHTTPServer(('localhost', port), BaseHTTPRequestHandler)
        server.timeout = 30

        server.handle_request()
        success_tracker.setdefault('server_success', True)

    client_thread = gevent.spawn(_do_client)
    server_thread = gevent.spawn(_do_server)

    try:
        with gevent.Timeout(5):
            while 'client_success' not in success_tracker and 'server_success' not in success_tracker:
                gevent.sleep(random.random())
    except gevent.Timeout:
        pass

    assert 'client_success' in success_tracker
    assert success_tracker['client_success'] is True

    assert 'server_success' in success_tracker
    assert success_tracker['server_success'] is True


def test_wait_for_connection_success():
    success_tracker = {}
    port = get_open_port()

    def _do_client():
        try:
            wait_for_connection('localhost', port, 2)
        except gevent.Timeout:
            success_tracker['client_success'] = False
        else:
            success_tracker['client_success'] = True

    client_thread = gevent.spawn(_do_client)

    try:
        with gevent.Timeout(5):
            while 'client_success' not in success_tracker:
                gevent.sleep(random.random())
    except gevent.Timeout:
        pass

    assert 'client_success' in success_tracker
    assert success_tracker['client_success'] is False
