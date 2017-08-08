from __future__ import absolute_import

import gevent_monkeypatch  # noqa: F401

import os

import pytest

import shutil
import itertools

from populus import Project

from populus.utils.chains import (
    get_base_blockchain_storage_dir,
)
from populus.utils.compile import (
    get_contracts_source_dir,
    get_build_asset_dir,
)
from populus.utils.filesystem import (
    ensure_path_exists,
)
from populus.utils.testing import (
    get_tests_dir,
    link_bytecode_by_name,
)


POPULUS_SOURCE_ROOT = os.path.dirname(__file__)


@pytest.fixture()
def temporary_dir(tmpdir):
    _temporary_dir = str(tmpdir.mkdir("temporary-dir"))
    return _temporary_dir


@pytest.fixture()
def project_dir(tmpdir, monkeypatch):
    _project_dir = str(tmpdir.mkdir("project-dir"))

    # setup project directories
    ensure_path_exists(get_contracts_source_dir(_project_dir))
    ensure_path_exists(get_build_asset_dir(_project_dir))
    ensure_path_exists(get_base_blockchain_storage_dir(_project_dir))

    monkeypatch.chdir(_project_dir)
    monkeypatch.syspath_prepend(_project_dir)

    return _project_dir


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
def _loaded_contract_fixtures(project_dir, request):
    contracts_to_load_from_fn = getattr(request.function, '_populus_contract_fixtures', [])
    contracts_to_load_from_module = getattr(request.module, '_populus_contract_fixtures', [])

    contracts_to_load = itertools.chain(
        contracts_to_load_from_fn,
        contracts_to_load_from_module,
    )
    contracts_source_dir = get_contracts_source_dir(project_dir)

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
    test_contracts_to_load_from_fn = getattr(request.function, '_populus_test_contract_fixtures', [])
    test_contracts_to_load_from_module = getattr(request.module, '_populus_test_contract_fixtures', [])

    test_contracts_to_load = itertools.chain(
        test_contracts_to_load_from_fn,
        test_contracts_to_load_from_module,
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


EXAMPLE_PACKAGES_BASE_PATH = './tests/example-packages'


@pytest.fixture()
def _loaded_installed_dependencies(populus_source_root, project_dir, request):
    from populus.utils.dependencies import (
        get_installed_packages_dir,
    )
    from populus.utils.filesystem import (
        find_solidity_source_files,
    )
    from populus.utils.packaging import (
        load_release_lockfile,
        extract_package_metadata,
    )
    from populus.utils.ipfs import (
        generate_file_hash,
    )
    from populus.packages.installation import (
        write_installed_packages,
    )

    packages_to_load_from_fn = getattr(request.function, '_populus_packages_to_load', [])
    packages_to_load_from_module = getattr(request.module, '_populus_packages_to_load', [])

    packages_to_load = itertools.chain(
        packages_to_load_from_fn,
        packages_to_load_from_module,
    )

    def load_example_package_data(example_package_name):
        example_package_dir = os.path.join(
            populus_source_root,
            EXAMPLE_PACKAGES_BASE_PATH,
            example_package_name,
        )

        if not os.path.exists(example_package_dir):
            raise ValueError(
                "Unable to load example package '{0}".format(example_package_name)
            )

        release_lockfile_path = os.path.join(example_package_dir, '1.0.0.json')
        release_lockfile_uri = generate_file_hash(release_lockfile_path)
        release_lockfile = load_release_lockfile(release_lockfile_path)
        source_file_paths = find_solidity_source_files(example_package_dir)
        source_tree = {
            os.path.relpath(source_file_path, example_package_dir): open(source_file_path).read()
            for source_file_path
            in source_file_paths
        }
        package_meta = extract_package_metadata(
            [
                example_package_name,
                "{0}==1.0.0".format(example_package_name),
                release_lockfile_uri,
            ],
            release_lockfile,
        )
        package_dependencies = tuple(
            load_example_package_data(dependency_name)
            for dependency_name
            in release_lockfile.get('build_dependencies', {}).keys()
        )

        package_data = {
            'meta': package_meta,
            'lockfile': release_lockfile,
            'source_tree': source_tree,
            'dependencies': package_dependencies,
        }
        return package_data

    installed_packages_dir = get_installed_packages_dir(project_dir)

    package_data_to_install = tuple(
        load_example_package_data(item)
        for item
        in packages_to_load
    )
    write_installed_packages(installed_packages_dir, package_data_to_install)


@pytest.fixture()
def _updated_project_config(project_dir, request):
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


@pytest.fixture()
def project(project_dir,
            _loaded_contract_fixtures,
            _loaded_test_contract_fixtures,
            _loaded_installed_dependencies):
    return Project()


def pytest_fixture_setup(fixturedef, request):
    """
    Injects the following fixtures ahead of the `project` fixture.

    - project_dir
    - _loaded_contract_fixtures
    - _loaded_test_contract_fixtures
    """
    if fixturedef.argname == 'project':
        request.getfixturevalue('project_dir')
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
