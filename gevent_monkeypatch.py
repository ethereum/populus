import os

if os.environ.get('THREADING_BACKEND', 'stdlib') == 'gevent':
    from gevent import monkey
    monkey.patch_socket()
