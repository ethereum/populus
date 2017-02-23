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
    from populus.utils.contracts import (
        get_contracts_source_dir,
    )
    from populus.utils.filesystem import (
        ensure_path_exists,
    )

    contracts_to_load_from_fn = getattr(request.function, '_populus_contract_fixtures', [])
    contracts_to_load_from_module = getattr(request.module, '_populus_contract_fixtures', [])

    contracts_to_load = itertools.chain(
        contracts_to_load_from_fn,
        contracts_to_load_from_module,
    )
    contracts_source_dir = get_contracts_source_dir(project_dir)

    for item in contracts_to_load:
        ensure_path_exists(contracts_source_dir)

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

        dst_path = os.path.join(contracts_source_dir, os.path.basename(item))

        if os.path.exists(dst_path):
            raise ValueError("File already present at '{0}'".format(dst_path))

        shutil.copy(src_path, dst_path)


@pytest.fixture()
def _loaded_test_contract_fixtures(populus_source_root, project_dir, request):
    from populus.utils.testing import (
        get_tests_dir,
    )
    from populus.utils.filesystem import (
        ensure_path_exists,
    )

    test_contracts_to_load_from_fn = getattr(request.function, '_populus_test_contract_fixtures', [])
    test_contracts_to_load_from_module = getattr(request.module, '_populus_test_contract_fixtures', [])

    test_contracts_to_load = itertools.chain(
        test_contracts_to_load_from_fn,
        test_contracts_to_load_from_module,
    )

    tests_dir = get_tests_dir(project_dir)

    for item in test_contracts_to_load:
        ensure_path_exists(tests_dir)

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
            raise ValueError("Unable to load test contract '{0}'".format(item))

        dst_path = os.path.join(tests_dir, os.path.basename(item))

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
def project(project_dir,
            _loaded_contract_fixtures,
            _loaded_test_contract_fixtures,
            _loaded_installed_dependencies):
    return Project()


@pytest.fixture()
def populus_source_root():
    return os.path.dirname(__file__)
