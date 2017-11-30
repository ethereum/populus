import os

from populus.utils.filesystem import (
    ensure_file_exists,
)
from populus.utils.six import (
    queue,
)
from populus.utils.observers.observers_watchdog import DirWatcher


def test_watchdog_based_observer(temporary_dir):
    file_path_a = os.path.join(temporary_dir, 'file-a.txt')

    ensure_file_exists(file_path_a)

    change_queue = queue.Queue()

    def change_cb(*args):
        change_queue.put(args)

    watcher = DirWatcher(temporary_dir, change_cb)
    watcher.start()

    def empty_queue():
        while True:
            try:
                change_queue.get(False)
            except queue.Empty:
                break
            else:
                change_queue.task_done()

    def assert_event(*expected):
        actual = change_queue.get(block=True, timeout=2)
        assert actual == expected
        change_queue.task_done()

    empty_queue()

    # write existing root file
    with open(file_path_a, 'w') as file_a:
        file_a.write('test')
    assert_event(file_path_a, 'modified')
