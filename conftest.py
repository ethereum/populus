import os

if os.environ.get('THREADING_BACKEND', 'stdlib') == 'gevent':
    from gevent import monkey
    monkey.patch_socket()

import pytest  # noqa: E402

import shutil  # noqa: E402
import itertools  # noqa: E402

from populus import Project  # noqa: E402


@pytest.fixture()
def temporary_dir(tmpdir):
    _temporary_dir = str(tmpdir.mkdir("temporary-dir"))
    return _temporary_dir


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


@pytest.fixture()
def wait_for_unlock():
    from populus.utils.compat import (
        Timeout,
    )

    def _wait_for_unlock(web3):
        with Timeout(5) as timeout:
            while True:
                try:
                    web3.eth.sendTransaction({
                        'from': web3.eth.coinbase,
                        'to': web3.eth.coinbase,
                        'value': 1
                    })
                except ValueError:
                    timeout.check()
                else:
                    break
    return _wait_for_unlock


@pytest.fixture()
def _loaded_contract_fixtures(populus_source_root, project_dir, request):
    from populus.utils.filesystem import (
        get_contracts_dir,
    )

    contracts_to_load_from_fn = getattr(request.function, '_populus_contract_fixtures', [])
    contracts_to_load_from_module = getattr(request.module, '_populus_contract_fixtures', [])

    contracts_to_load = itertools.chain(
        contracts_to_load_from_fn,
        contracts_to_load_from_module,
    )

    for item in contracts_to_load:
        fixture_path = os.path.join(
            populus_source_root,
            'tests',
            'fixtures',
            item,
        )
        if os.path.exists(item):
            src_path = item
        elif os.path.exists(fixture_path):
            src_path = fixture_path
        else:
            raise ValueError("Unable to load contract '{0}'".format(item))

        dst_path = os.path.join(
            get_contracts_dir(project_dir),
            os.path.basename(item),
        )
        if os.path.exists(dst_path):
            raise ValueError("File already present at '{0}'".format(dst_path))

        shutil.copy(src_path, dst_path)


@pytest.fixture()
def project(project_dir, _loaded_contract_fixtures):
    return Project()


@pytest.fixture()
def populus_source_root():
    return os.path.dirname(__file__)
