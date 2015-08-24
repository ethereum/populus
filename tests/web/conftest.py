import os
import shutil
import pytest

from populus.web import get_build_assets_dir


PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'projects', 'test-01'))


@pytest.fixture(autouse=True)
def clear_build_assets():
    build_assets_path = get_build_assets_dir(PROJECT_DIR)
    if os.path.exists(build_assets_path):
        shutil.rmtree(build_assets_path)
