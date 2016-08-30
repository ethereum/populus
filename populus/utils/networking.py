import sys
import random

import gevent
from gevent import socket


if sys.version_info.major == 2:
    ConnectionRefusedError = socket.error


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def wait_for_connection(host, port, timeout=30):
    with gevent.Timeout(timeout):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.timeout = 1
            try:
                s.connect((host, port))
            except (socket.timeout, ConnectionRefusedError):
                gevent.sleep(random.random())
                continue
            else:
                break
        else:
            raise ValueError("Unable to establish HTTP connection")
