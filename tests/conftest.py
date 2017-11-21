from __future__ import absolute_import

import os

import pytest

import shutil
import itertools

from populus import Project
from populus.config.base import (
    Config,
)
from populus.config.helpers import (
    get_default_populus_config_path,
    get_default_project_config_path,
    get_populus_config_file_path,
    get_project_config_file_path,
    load_default_populus_config,
)

from populus.config.loading import (
    load_config,
    write_config,
)

from populus.config.versions import (
    LATEST_VERSION,
)
from populus.utils.compile import (
    get_contracts_source_dirs,
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
from populus.utils.mappings import (
    set_nested_key,
    delete_nested_key,
)
from populus.utils.wait import (
    Timeout,
)


POPULUS_SOURCE_ROOT = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture()
def populus_config_dir(tmpdir, monkeypatch):
    """
    Since populus uses the user's $HOME directory to house the populus config, we want to be sure that our tests are not using any configuration that's been written there.
    """
    _populus_config_dir = str(tmpdir.mkdir("populus-config"))
    monkeypatch.setenv('POPULUS_DIR', _populus_config_dir)
    return _populus_config_dir


@pytest.fixture()
def populus_config_path(populus_config_dir, request):
    if hasattr(request.function, '_populus_config_version'):
        config_version = getattr(request.function, '_populus_config_version')
    elif hasattr(request.module, '_populus_config_version'):
        config_version = getattr(request.module, '_populus_config_version')
    else:
        config_version = None

    config_file_path = get_populus_config_file_path()
    defaults_file_path = get_default_populus_config_path(config_version)

    populus_config = load_config(defaults_file_path)

    key_value_pairs_from_fn = getattr(request.function, '_populus_config_key_value_pairs', [])
    key_value_pairs_from_module = getattr(request.module, '_populus_config_key_value_pairs', [])

    key_value_pairs = tuple(itertools.chain(
        key_value_pairs_from_module,
        key_value_pairs_from_fn,
    ))

    for key, value in key_value_pairs:
        if value is None:
            delete_nested_key(populus_config, key)
        else:
            set_nested_key(populus_config, key, value)

    if key_value_pairs or config_version is not None:
        write_config(populus_config, config_file_path)
        return config_file_path
    else:
        # Since we have no custom configuration we can just let populus
        # fallback to the default latest version of the populus config.
        return None


@pytest.fixture()
def temporary_dir(tmpdir):
    _temporary_dir = str(tmpdir.mkdir("temporary-dir"))
    return _temporary_dir


@pytest.fixture()
def project_dir(tmpdir, monkeypatch):
    _project_dir = str(tmpdir.mkdir("project-dir"))

    monkeypatch.chdir(_project_dir)
    monkeypatch.syspath_prepend(_project_dir)

    return _project_dir


@pytest.fixture()
def project_config_path(project_dir, request):
    if hasattr(request.function, '_project_config_version'):
        config_version = getattr(request.function, '_project_config_version')
    elif hasattr(request.module, '_project_config_version'):
        config_version = getattr(request.module, '_project_config_version')
    else:
        config_version = LATEST_VERSION

    config_file_path = get_project_config_file_path(project_dir)
    defaults_file_path = get_default_project_config_path(config_version)

    project_config = load_config(defaults_file_path)

    # setup any module or test specific configuration
    key_value_pairs_from_fn = getattr(request.function, '_project_config_key_value_pairs', [])
    key_value_pairs_from_module = getattr(request.module, '_project_config_key_value_pairs', [])

    key_value_pairs = tuple(itertools.chain(
        key_value_pairs_from_module,
        key_value_pairs_from_fn,
    ))

    for key, value in key_value_pairs:
        if value is None:
            delete_nested_key(project_config, key)
        else:
            set_nested_key(project_config, key, value)

    # write the project config to disk
    write_config(project_config, config_file_path)

    return config_file_path


CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"


@pytest.fixture()
def project(request,
            project_dir,
            populus_config_path,
            project_config_path,
            _loaded_contract_fixtures,
            _loaded_test_contract_fixtures):
    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)

    project = Project(
        project_dir=project_dir,
        populus_config_file_path=populus_config_path,
    )

    # TODO: is this still necessary?  Seems like we set the cache *every* run
    # which is a lot of overhead.
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
def populus_config_defaults():
    return Config(load_default_populus_config())


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
