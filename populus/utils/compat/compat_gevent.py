import collections

import gevent
from gevent.pywsgi import (  # noqa: F401
    WSGIServer,
)
from gevent import (  # noqa: F401
    subprocess,
    socket,
    threading,
)

import pylru

from geventhttpclient import HTTPClient


_client_cache = pylru.lrucache(8)


sleep = gevent.sleep
spawn = gevent.spawn
GreenletThread = gevent.Greenlet


class Timeout(gevent.Timeout):
    def check(self):
        pass

    def sleep(self, seconds):
        gevent.sleep(seconds)


def make_server(host, port, application, *args, **kwargs):
    server = WSGIServer((host, port), application, *args, **kwargs)
    return server


def _get_client(host, port, **kwargs):
    ordered_kwargs = collections.OrderedDict(sorted(kwargs.items()))
    cache_key = '{0}:{1}:{2}'.format(
        host,
        port,
        ':'.join((
            "{0}={1}".format(str(key), str(value))
            for key, value in ordered_kwargs.items()
        ))
    )
    if cache_key not in _client_cache:
        _client_cache[cache_key] = HTTPClient(host, port, **kwargs)
    return _client_cache[cache_key]
