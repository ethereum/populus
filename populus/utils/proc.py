import random
import signal

from populus.utils.compat import Timeout


def wait_for_popen(proc, max_wait=5):
    with Timeout(max_wait) as timeout:
        while True:
            if proc.poll() is None:
                timeout.sleep(random.random())
            else:
                break


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
