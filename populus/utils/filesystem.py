import contextlib
import errno
import fnmatch
import functools
import os
import shutil
import sys
import tempfile as _tempfile

from eth_utils import (
    to_tuple,
)


if sys.version_info.major == 2:
    FileNotFoundError = OSError


def ensure_path_exists(dir_path):
    """
    Make sure that a path exists
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return True
    return False


def ensure_file_exists(file_path):
    """
    Make sure that a path exists
    """
    if os.path.exists(file_path):
        return False
    base_dir = os.path.dirname(file_path)
    ensure_path_exists(base_dir)
    with open(file_path, 'w'):
        pass
    return True


def remove_file_if_exists(path):
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False


def remove_dir_if_exists(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        return True
    return False


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def is_executable_available(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.dirname(program)
    if fpath:
        if is_exe(program):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True

    return False


@to_tuple
def recursive_find_files(base_dir, pattern):
    for dirpath, _, filenames in os.walk(base_dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                yield os.path.join(dirpath, filename)


@to_tuple
def find_solidity_source_files(base_dir):
    return (
        os.path.relpath(source_file_path)
        for source_file_path
        in recursive_find_files(base_dir, "*.sol")
    )


@to_tuple
def find_solidity_test_files(base_dir):
    return (
        os.path.relpath(source_file_path)
        for source_file_path
        in recursive_find_files(base_dir, "Test*.sol")
    )


@contextlib.contextmanager
def tempdir(*args, **kwargs):
    directory = _tempfile.mkdtemp(*args, **kwargs)

    try:
        yield directory
    finally:
        remove_dir_if_exists(directory)


@contextlib.contextmanager
def tempfile(*args, **kwargs):
    _, file_path = _tempfile.mkstemp(*args, **kwargs)

    try:
        yield file_path
    finally:
        remove_file_if_exists(file_path)


def is_same_path(p1, p2):
    n_p1 = os.path.abspath(os.path.expanduser(p1))
    n_p2 = os.path.abspath(os.path.expanduser(p2))

    try:
        return os.path.samefile(n_p1, n_p2)
    except FileNotFoundError:
        return n_p1 == n_p2


def relpath(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        path = fn(*args, **kwargs)
        return os.path.relpath(path)
    return wrapper


def normpath(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        path = fn(*args, **kwargs)
        return os.path.normpath(path)
    return wrapper


def is_under_path(base_path, path):
    if is_same_path(base_path, path):
        return False
    absolute_base_path = os.path.abspath(base_path)
    absolute_path = os.path.abspath(path)
    return absolute_path.startswith(absolute_base_path)
