import signal

from .wait import (
    wait_for_popen,
)


def kill_proc(proc):
    try:
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            wait_for_popen(proc, 5)
        if proc.poll() is None:
            proc.terminate()
            wait_for_popen(proc, 2)
        if proc.poll() is None:
            proc.kill()
            wait_for_popen(proc, 1)
    except KeyboardInterrupt:
        proc.kill()
