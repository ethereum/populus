import pytest

import os

from populus.utils.filesystem import (
    ensure_file_exists,
)


def is_gevent_enabled():
    return os.environ.get('THREADING_BACKEND', 'stdlib') == 'gevent'


@pytest.mark.skipif(not is_gevent_enabled(), reason="missing gevent dependency")
def test_gevent_based_observer(temporary_dir):
    from populus.utils.observers.observers_gevent import DirWatcher
    import gevent
    from gevent import queue

    file_path_a = os.path.join(temporary_dir, 'file-a.txt')

    ensure_file_exists(file_path_a)

    change_queue = queue.JoinableQueue()

    def change_cb(*args):
        change_queue.put(args)

    watcher = DirWatcher(temporary_dir, change_cb)
    watcher.start()

    def empty_queue():
        while True:
            try:
                gevent.sleep(1)
                change_queue.get(False)
            except queue.Empty:
                break
            else:
                change_queue.task_done()

    def assert_event(*expected):
        gevent.sleep(1)
        actual = change_queue.get(block=True, timeout=2)
        assert actual == expected
        change_queue.task_done()

    empty_queue()

    # write existing root file
    with open(file_path_a, 'w') as file_a:
        file_a.write('test')
    assert_event(file_path_a, 'modified')
