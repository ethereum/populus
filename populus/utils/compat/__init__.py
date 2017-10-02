import os
import warnings


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
    warn_msg = ("Support for gevent will be dropped in the next populus version"
                "Please use to gevent.monkey instead"
                )
    warnings.warn(warn_msg, DeprecationWarning)
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
