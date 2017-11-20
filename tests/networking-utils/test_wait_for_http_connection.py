import random
import threading

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
from populus.utils.wait import (
    Timeout,
)


def _spawn(target, *args, **kwargs):
    thread = threading.Thread(
        target=target,
        args=args,
        kwargs=kwargs,
    )
    thread.daemon = True
    thread.start()
    return thread


def test_wait_for_connection_success():
    success_tracker = {}
    port = get_open_port()

    def _do_client():
        success_tracker['client_booted'] = True
        try:
            wait_for_connection('localhost', port)
        except Timeout:
            success_tracker['client_success'] = False
        else:
            success_tracker['client_success'] = True
        finally:
            success_tracker['client_exited'] = True

    class TestHTTPServer(HTTPServer):
        timeout = 30

        def handle_timeout(self):
            success_tracker['server_success'] = False

        def handle_error(self):
            success_tracker['server_success'] = True

    def _do_server():
        success_tracker['server_booted'] = True
        server = TestHTTPServer(('localhost', port), BaseHTTPRequestHandler)
        server.timeout = 30

        success_tracker['server_before_handle'] = True
        server.handle_request()
        success_tracker['server_after_handle'] = True
        success_tracker.setdefault('server_success', True)
        success_tracker['server_exited'] = True

    _spawn(_do_client)
    _spawn(_do_server)

    try:
        with Timeout(5) as _timeout:
            while 'client_success' not in success_tracker and 'server_success' not in success_tracker:  # noqa: E501
                _timeout.sleep(0.01)
    except Timeout:
        pass

    assert 'client_success' in success_tracker
    assert success_tracker['client_success'] is True

    assert 'server_success' in success_tracker
    assert success_tracker['server_success'] is True


def test_wait_for_connection_failure():
    success_tracker = {}
    port = get_open_port()

    def _do_client():
        success_tracker['client_booted'] = True
        try:
            wait_for_connection('localhost', port, 2)
        except Timeout:
            success_tracker['client_success'] = False
        else:
            success_tracker['client_success'] = True

    _spawn(_do_client)

    try:
        with Timeout(5) as _timeout:
            while 'client_success' not in success_tracker:
                _timeout.sleep(random.random())
    except Timeout:
        pass

    assert 'client_success' in success_tracker
    assert success_tracker['client_success'] is False
