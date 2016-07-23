import gevent
import random
import requests


def get_open_port():
    s = gevent.socket.socket(gevent.socket.AF_INET, gevent.socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def wait_for_http_connection(host, port, timeout=30):
    with gevent.Timeout(timeout):
        while True:
            try:
                requests.post("http://{0}:{1}".format(host, port))
            except requests.ConnectionError:
                gevent.sleep(random.random())
                continue
            else:
                break
        else:
            raise ValueError("Unable to establish HTTP connection")
