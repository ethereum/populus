import os
import shutil
import fnmatch
import tempfile
import contextlib


def ensure_path_exists(dir_path):
    """
    Make sure that a path exists
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return True
    return False


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


CONTRACTS_DIR = "./contracts/"


def get_contracts_dir(project_dir):
    contracts_dir = os.path.join(project_dir, CONTRACTS_DIR)
    return os.path.abspath(contracts_dir)


BUILD_DIR = "./build/"


def get_build_dir(project_dir):
    build_dir = os.path.join(project_dir, BUILD_DIR)
    ensure_path_exists(build_dir)
    return build_dir


COMPILED_CONTRACTS_FILENAME = "contracts.json"


def get_compiled_contracts_destination_path(project_dir):
    build_dir = get_build_dir(project_dir)
    return os.path.join(build_dir, COMPILED_CONTRACTS_FILENAME)


BLOCKCHAIN_DIR = "./chains/"


def get_blockchains_dir(project_dir):
    blockchains_dir = os.path.abspath(os.path.join(project_dir, BLOCKCHAIN_DIR))
    ensure_path_exists(blockchains_dir)
    return blockchains_dir


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


def recursive_find_files(base_dir, pattern):
    for dirpath, _, filenames in os.walk(base_dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                yield os.path.join(dirpath, filename)


@contextlib.contextmanager
def tempdir():
    directory = tempfile.mkdtemp()

    try:
        yield directory
    finally:
        shutil.rmtree(directory)
