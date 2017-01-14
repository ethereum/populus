import random

from .compat import (
    socket,
    Timeout,
)


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def wait_for_connection(host, port, timeout=30):
    with Timeout(timeout) as _timeout:
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            try:
                s.connect((host, port))
            except (socket.timeout, socket.error, OSError):
                _timeout.sleep(random.random())
                continue
            else:
                s.close()
                break
        else:
            raise ValueError("Unable to establish HTTP connection")
