"""
From: https://gist.github.com/fpom/92a690a8cf89cebd7d4a
"""
import os
import collections
import gevent
from gevent import pool
from gevent import queue


event = collections.namedtuple("event", ["name", "path", "isdir"])


class DirWatcher (object):
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.pool = pool.Pool()
        self.q = queue.Queue()
        self.w = {}
        self.add(root, "crawl")

    def get(self):
        return self.q.get()

    def add(self, path, evt="create"):
        if os.path.isdir(path):
            for name in os.listdir(path):
                self.add(os.path.join(path, name), evt)
        self.pool.spawn(self.watch, path)
        self.q.put(event(evt, path, os.path.isdir(path)))

    def watch(self, path):
        hub = gevent.get_hub()
        watcher = hub.loop.stat(path, 1)
        self.w[path] = watcher
        isdir = os.path.isdir(path)
        if isdir:
            old = set(os.listdir(path))
        while path in self.w:
            try:
                with gevent.Timeout(2):
                    hub.wait(watcher)
            except:
                continue
            if os.path.isdir(path):
                new = set(os.listdir(path))
                for name in new - old:
                    self.add(os.path.join(path, name))
                old = new
            elif os.path.exists(path):
                self.q.put(event("update", path, isdir))
            else:
                break
        if isdir:
            for name in old:
                self.w.pop(os.path.join(path, name), None)
        self.w.pop(path, None)
        self.q.put(event("delete", path, isdir))
