import pytest

import os

from populus.compilation import (
    compile_and_write_contracts,
)
from populus.solidity import (
    is_solc_available,
)

skip_if_no_sol_compiler = pytest.mark.skipif(
    not is_solc_available(),
    reason="'solc' compiler not available",
)


BASE_DIR= os.path.abspath(os.path.dirname(__file__))

project_dir = os.path.join(BASE_DIR, 'projects', 'test-01')


@pytest.fixture(autouse=True)
def _project_dir(monkeypatch):
    monkeypatch.chdir(project_dir)
    return project_dir


@skip_if_no_sol_compiler
def test_compilation():
    compile_and_write_contracts(project_dir)
