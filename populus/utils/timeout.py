import time


class Timeout(Exception):
    """
    A limited subset of the `gevent.Timeout` context manager.
    """
    seconds = None
    exception = None
    begun_at = None
    is_running = None

    def __init__(self, seconds=None, exception=None, *args, **kwargs):
        self.seconds = seconds
        self.exception = exception

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __str__(self):
        if self.seconds is None:
            return ''
        return "{0} seconds".format(self.seconds)

    @property
    def expire_at(self):
        if self.seconds is None:
            raise ValueError("Timeouts with `seconds == None` do not have an expiration time")
        elif self.begun_at is None:
            raise ValueError("Timeout has not been started")
        return self.begun_at + self.seconds

    def start(self):
        if self.is_running is not None:
            raise ValueError("Timeout has already been started")
        self.begun_at = time.time()
        self.is_running = True

    def check(self):
        if self.is_running is None:
            raise ValueError("Timeout has not been started")
        elif self.is_running is False:
            raise ValueError("Timeout has already been cancelled")
        elif self.seconds is None:
            return
        elif time.time() > self.expire_at:
            self.is_running = False
            if isinstance(self.exception, type):
                raise self.exception(str(self))
            elif isinstance(self.exception, Exception):
                raise self.exception
            else:
                raise self

    def cancel(self):
        self.is_running = False

    def sleep(self, seconds):
        time.sleep(seconds)
        self.check()
