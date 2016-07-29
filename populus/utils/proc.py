import random
import signal

import gevent


def wait_for_popen(proc, max_wait=5):
    with gevent.Timeout(max_wait):
        while True:
            if proc.poll() is None:
                gevent.sleep(random.random())
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
