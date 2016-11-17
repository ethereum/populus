import os

import pytest


@pytest.fixture()
def project_dir(tmpdir, monkeypatch):
    from populus.utils.filesystem import (
        ensure_path_exists,
    )
    from populus.utils.contracts import (
        get_contracts_source_dir,
    )
    from populus.utils.chains import (
        get_base_blockchain_storage_dir,
    )

    _project_dir = str(tmpdir.mkdir("project-dir"))

    # setup project directories
    ensure_path_exists(get_contracts_source_dir(_project_dir))
    ensure_path_exists(get_base_blockchain_storage_dir(_project_dir))

    monkeypatch.chdir(_project_dir)
    monkeypatch.syspath_prepend(_project_dir)

    return _project_dir


@pytest.fixture()
def write_project_file(project_dir):
    from populus.utils.filesystem import (
        ensure_path_exists,
    )

    def _write_project_file(filename, content=''):
        full_path = os.path.join(project_dir, filename)
        file_dir = os.path.dirname(full_path)
        ensure_path_exists(file_dir)

        with open(full_path, 'w') as f:
            f.write(content)
    return _write_project_file
