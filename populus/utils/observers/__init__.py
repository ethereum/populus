import os


def get_observer_backend():
    if 'POPULUS_THREADING_BACKEND' in os.environ:
        return os.environ['POPULUS_THREADING_BACKEND']
    elif 'THREADING_BACKEND' in os.environ:
        return os.environ['THREADING_BACKEND']
    else:
        return 'watchdog'


OBSERVER_BACKEND = get_observer_backend()


if OBSERVER_BACKEND == 'watchdog':
    from .observers_watchdog import (
        # TODO: implement this.
        DirWatcher,
    )
elif OBSERVER_BACKEND == 'gevent':
    from .observers_gevent import (  # noqa: F401
        DirWatcher,
    )
else:
    raise ValueError("Unsupported observer backend.  Must be one of 'gevent' or 'observer'")
