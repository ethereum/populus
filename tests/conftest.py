from __future__ import absolute_import

import os

import pytest

import shutil
import itertools

from populus import Project

from populus.utils.chains import (
    get_base_blockchain_storage_dir,
)
from populus.utils.compile import (
    get_contracts_source_dirs,
    get_build_asset_dir,
)
from populus.utils.filesystem import (
    ensure_path_exists,
    get_latest_mtime,
)
from populus.utils.testing import (
    get_tests_dir,
    link_bytecode_by_name,
)

from populus.utils.json import (
    normalize_object_for_json,
)

from populus.utils.contracts import (
    package_contracts,
)

from populus.config.defaults import (
    load_user_default_config,
)
from populus.utils.wait import (
    Timeout,
)

from populus.config.base import (
    Config,
)

from populus.config.helpers import (
    get_user_json_config_file_path,
)

from populus.config.defaults import (
    get_user_default_config_path,
)

from populus.config.versions import (
    LATEST_VERSION,
)

POPULUS_SOURCE_ROOT = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(autouse=True)
def user_base_path(tmpdir, monkeypatch):
    """
    Prevent tests from running against the config file found at
    `~/.populus/config`
    """
    tmp_user_base_path = str(tmpdir.mkdir('populus-home'))
    monkeypatch.setenv('POPULUS_USER_BASE_PATH', tmp_user_base_path)
    return tmp_user_base_path


@pytest.fixture()
def temporary_dir(tmpdir):
    _temporary_dir = str(tmpdir.mkdir("temporary-dir"))
    return _temporary_dir


@pytest.fixture()
def project_dir(tmpdir, monkeypatch):
    _project_dir = str(tmpdir.mkdir("project-dir"))

    # setup project directories
    for source_dir in get_contracts_source_dirs(_project_dir):
        ensure_path_exists(source_dir)
    ensure_path_exists(get_build_asset_dir(_project_dir))
    ensure_path_exists(get_base_blockchain_storage_dir(_project_dir))

    monkeypatch.chdir(_project_dir)
    monkeypatch.syspath_prepend(_project_dir)

    return _project_dir


@pytest.fixture()
def user_config_path(tmpdir, request):

    version = getattr(request.function, '_user_config_version', LATEST_VERSION)
    tmp_user_config_path = tmpdir.join(os.path.basename(get_user_json_config_file_path())).strpath
    user_defaults_path = get_user_default_config_path(version)
    shutil.copyfile(user_defaults_path, tmp_user_config_path)

    return tmp_user_config_path


CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"


@pytest.fixture()
def project(request,
            project_dir,
            user_config_path,
            _loaded_contract_fixtures,
            _loaded_test_contract_fixtures):

    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)

    project = Project(
        project_dir=project_dir,
        user_config_file_path=user_config_path,
    )

    key_value_pairs_from_fn = getattr(request.function, '_populus_config_key_value_pairs', [])
    key_value_pairs_from_module = getattr(request.module, '_populus_config_key_value_pairs', [])

    key_value_pairs = tuple(itertools.chain(
        key_value_pairs_from_module,
        key_value_pairs_from_fn,
    ))

    for key, value in key_value_pairs:
        if value is None:
            del project.config[key]
        else:
            project.config[key] = value

    project.fill_contracts_cache(contracts, mtime)
    request.config.cache.set(
        CACHE_KEY_CONTRACTS,
        normalize_object_for_json(project.compiled_contract_data),
    )
    request.config.cache.set(
        CACHE_KEY_MTIME,
        get_latest_mtime(project.get_all_source_file_paths()),
    )

    return project


@pytest.yield_fixture()
def chain(project):
    with project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def registrar(chain):
    return chain.registrar


@pytest.fixture()
def provider(chain):
    return chain.provider


@pytest.fixture()
def web3(chain):
    return chain.web3


@pytest.fixture()
def base_contract_factories(chain):
    return package_contracts({
        contract_name: chain.provider.get_base_contract_factory(contract_name)
        for contract_name in chain.provider.get_all_contract_names()
    })


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts


@pytest.fixture()
def write_project_file(project_dir):
    def _write_project_file(filename, content=''):
        full_path = os.path.join(project_dir, filename)
        file_dir = os.path.dirname(full_path)
        ensure_path_exists(file_dir)

        with open(full_path, 'w') as f:
            f.write(content)
    return _write_project_file


@pytest.fixture
def user_config_defaults():
    return Config(load_user_default_config())


@pytest.fixture()
def wait_for_unlock():
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
def _loaded_contract_fixtures(project_dir, request):
    contracts_to_load_from_fn = getattr(request.function, '_populus_contract_fixtures', [])
    contracts_to_load_from_module = getattr(request.module, '_populus_contract_fixtures', [])

    contracts_to_load = itertools.chain(
        contracts_to_load_from_module,
        contracts_to_load_from_fn,
    )
    contracts_source_dir = get_contracts_source_dirs(project_dir)[0]

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
def _loaded_test_contract_fixtures(project_dir, request):
    test_contracts_to_load_from_fn = getattr(
        request.function, '_populus_test_contract_fixtures',
        []
    )
    test_contracts_to_load_from_module = getattr(
        request.module, '_populus_test_contract_fixtures',
        []
    )

    test_contracts_to_load = itertools.chain(
        test_contracts_to_load_from_module,
        test_contracts_to_load_from_fn,
    )

    tests_dir = get_tests_dir(project_dir)

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
def math(chain):
    Math = chain.provider.get_contract_factory('Math')

    math_address = chain.wait.for_contract_address(Math.constructor().transact())

    return Math(address=math_address)


@pytest.fixture()
def library_13(chain):
    Library13 = chain.provider.get_contract_factory('Library13')

    library_13_address = chain.wait.for_contract_address(Library13.constructor().transact())

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

    multiply_13_address = chain.wait.for_contract_address(LinkedMultiply13.constructor().transact())

    return LinkedMultiply13(address=multiply_13_address)
