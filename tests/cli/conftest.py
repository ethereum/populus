import os
import shutil

import pytest


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(autouse=True)
def cleanup_build_dirs():
    """
    Remove the build dirs that are created during test runs.
    """
    build_dir = os.path.join(BASE_DIR, './projects/test-01/build/')
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
