from __future__ import absolute_import

import gevent_monkeypatch  # noqa: F401

import os

import pytest

import shutil
import itertools

from populus import api
from populus import Project

from populus.utils.geth import (
    get_base_blockchain_storage_dir,
)
from populus.utils.filesystem import (
    ensure_path_exists,
)
from populus.utils.testing import (
    link_bytecode_by_name,
)

from populus import ASSETS_DIR

from populus.defaults import (
    DEFAULT_CONTRACTS_DIR,
    DEFAULT_TESTS_DIR,
    BUILD_ASSET_DIR,
    USER_JSON_CONFIG_DEFAULTS,

)

from populus.api.config import (
    load_user_config,
)


POPULUS_SOURCE_ROOT = os.path.dirname(__file__)


@pytest.fixture()
def temporary_dir(tmpdir):
    _temporary_dir = str(tmpdir.mkdir("temporary-dir"))
    return _temporary_dir


@pytest.fixture()
def user_config_path(temporary_dir):
    _user_config_path = os.path.join(temporary_dir, USER_JSON_CONFIG_DEFAULTS)
    if not os.path.exists(_user_config_path):
        shutil.copyfile(
            os.path.join(ASSETS_DIR, USER_JSON_CONFIG_DEFAULTS),
            _user_config_path
        )
    return _user_config_path


@pytest.fixture()
def user_config(user_config_path):
    return load_user_config(user_config_path)


@pytest.fixture()
def project(tmpdir, user_config_path, monkeypatch):
    project_dir = str(tmpdir.mkdir("project-dir"))
    project = api.project.init_project(
        project_dir,
        user_config_path,
    )

    dirs = (DEFAULT_CONTRACTS_DIR, DEFAULT_TESTS_DIR, BUILD_ASSET_DIR,)
    for dir_name in dirs:
        assert (
            os.path.exists(
                os.path.join(project.project_root_dir, dir_name)
                )
        )

    monkeypatch.chdir(project_dir)
    monkeypatch.syspath_prepend(project_dir)

    return project


@pytest.fixture()
def _project_loaded(project):

    pass


@pytest.fixture()
def write_project_file(project_dir):
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
def _loaded_contract_fixtures(project, request):
    contracts_to_load_from_fn = getattr(request.function, '_populus_contract_fixtures', [])
    contracts_to_load_from_module = getattr(request.module, '_populus_contract_fixtures', [])

    contracts_to_load = itertools.chain(
        contracts_to_load_from_fn,
        contracts_to_load_from_module,
    )
    contracts_source_dir = project.contracts_source_dir

    for item, dst_path in contracts_to_load:
        ensure_path_exists(contracts_source_dir)

        fixture_path = os.path.join(
            POPULUS_SOURCE_ROOT,
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

        if dst_path is None:
            dst_path = os.path.join(contracts_source_dir, os.path.basename(item))
        elif not os.path.isabs(dst_path):
            dst_path = os.path.join(project_dir, dst_path)

        ensure_path_exists(os.path.dirname(dst_path))

        if os.path.exists(dst_path):
            raise ValueError("File already present at '{0}'".format(dst_path))

        shutil.copy(src_path, dst_path)


@pytest.fixture()
def _loaded_test_contract_fixtures(project, request):
    test_contracts_to_load_from_fn = getattr(request.function, '_populus_test_contract_fixtures', [])
    test_contracts_to_load_from_module = getattr(request.module, '_populus_test_contract_fixtures', [])

    test_contracts_to_load = itertools.chain(
        test_contracts_to_load_from_fn,
        test_contracts_to_load_from_module,
    )

    tests_dir = project.tests_dir

    for item, dst_path in test_contracts_to_load:
        ensure_path_exists(tests_dir)

        fixture_path = os.path.join(
            POPULUS_SOURCE_ROOT,
            'tests',
            'fixtures',
            item,
        )
        if os.path.exists(item):
            src_path = item
        elif os.path.exists(fixture_path):
            src_path = fixture_path
        else:
            raise ValueError("Unable to load test contract '{0}'".format(item))

        if dst_path is None:
            dst_path = os.path.join(tests_dir, os.path.basename(item))
        elif not os.path.isabs(dst_path):
            dst_path = os.path.join(project_dir, dst_path)

        ensure_path_exists(os.path.dirname(dst_path))

        if os.path.exists(dst_path):
            raise ValueError("File already present at '{0}'".format(dst_path))

        shutil.copy(src_path, dst_path)


@pytest.fixture()
def _updated_project_config(project, request):
    key_value_pairs_from_fn = getattr(request.function, '_populus_config_key_value_pairs', [])
    key_value_pairs_from_module = getattr(request.module, '_populus_config_key_value_pairs', [])

    key_value_pairs = tuple(itertools.chain(
        key_value_pairs_from_fn,
        key_value_pairs_from_module,
    ))

    if key_value_pairs:
        project = Project()

        for key, value in key_value_pairs:
            if value is None:
                del project.config[key]
            else:
                project.config[key] = value

        project.write_config()


def pytest_fixture_setup(fixturedef, request):
    """
    Injects the following fixtures ahead of the `project` fixture.

    - project
    - _loaded_contract_fixtures
    - _loaded_test_contract_fixtures
    """

    if fixturedef.argname == "_project_loaded":
        request.getfixturevalue('user_config')
        request.getfixturevalue('_loaded_contract_fixtures')
        request.getfixturevalue('_loaded_test_contract_fixtures')
        request.getfixturevalue('_updated_project_config')


@pytest.fixture()
def math(chain):
    Math = chain.provider.get_contract_factory('Math')

    math_address = chain.wait.for_contract_address(Math.deploy())

    return Math(address=math_address)


@pytest.fixture()
def library_13(chain):
    Library13 = chain.provider.get_contract_factory('Library13')

    library_13_address = chain.wait.for_contract_address(Library13.deploy())

    return Library13(address=library_13_address)


@pytest.fixture()
def multiply_13(chain, library_13):
    Multiply13 = chain.project.compiled_contract_data['Multiply13']

    bytecode = link_bytecode_by_name(
        Multiply13['bytecode'],
        Multiply13['linkrefs'],
        Library13=library_13.address,
    )

    LinkedMultiply13 = chain.web3.eth.contract(
        abi=Multiply13['abi'],
        bytecode=bytecode,
    )

    multiply_13_address = chain.wait.for_contract_address(LinkedMultiply13.deploy())

    return LinkedMultiply13(address=multiply_13_address)
