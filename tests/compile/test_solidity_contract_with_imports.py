import pytest

import os

from populus.compilation import (
    compile_and_write_contracts,
)


BASE_DIR= os.path.abspath(os.path.dirname(__file__))

project_dir = os.path.join(BASE_DIR, 'projects', 'test-01')


@pytest.fixture(autouse=True)
def _project_dir(monkeypatch):
    monkeypatch.chdir(project_dir)
    return project_dir


def test_compilation():
    compile_and_write_contracts(project_dir)
