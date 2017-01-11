import os


def get_threading_backend():
    if 'POPULUS_THREADING_BACKEND' in os.environ:
        return os.environ['POPULUS_THREADING_BACKEND']
    elif 'THREADING_BACKEND' in os.environ:
        return os.environ['THREADING_BACKEND']
    else:
        return 'stdlib'


THREADING_BACKEND = get_threading_backend()


if THREADING_BACKEND == 'stdlib':
    from .compat_stdlib import (
        Timeout,
        sleep,
        socket,
        threading,
        make_server,
        GreenletThread,
        spawn,
        subprocess,
    )
elif THREADING_BACKEND == 'gevent':
    from .compat_gevent import (  # noqa: F401
        Timeout,
        sleep,
        socket,
        threading,
        make_server,
        GreenletThread,
        spawn,
        subprocess,
    )
else:
    raise ValueError("Unsupported threading backend.  Must be one of 'gevent' or 'stdlib'")
