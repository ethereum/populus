import sys

from watchdog.utils import UnsupportedLibc
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler


def get_observer_for_platform(platform):
    if platform == 'darwin':
        from watchdog.observers.kqueue import KqueueObserver
        return KqueueObserver
    elif platform.startswith('linux'):
        try:
            from watchdog.observers.inotify import (
                InotifyObserver,
            )
        except UnsupportedLibc:
            return PollingObserver
        else:
            return InotifyObserver
    elif platform in {'win32', 'cygwin'}:
        from watchdog.observers.read_directory_changes import WindowsAPIObserver
        return WindowsAPIObserver
    else:
        raise ValueError(
            "Unsupported platfom '{0}'.  Must be one of 'win32', 'cgwin', "
            "'linux*', 'darwin'"
        )


class EventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_any_event(self, event):
        self.callback(event.src_path, event.event_type)


class DirWatcher(object):
    def __init__(self, path_to_watch, callback, observer_class=None):
        if observer_class is None:
            observer_class = get_observer_for_platform(sys.platform)
        self.observer = observer_class()
        self.event_handler = EventHandler(callback)
        self.observer.schedule(self.event_handler, path_to_watch, recursive=True)

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
