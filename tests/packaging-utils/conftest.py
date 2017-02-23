import pytest

import os
import json
from collections import OrderedDict

from eth_utils import (
    to_dict,
)

from populus import Project

from populus.packages.backends.ipfs import BaseIPFSPackageBackend
from populus.packages.backends.index import BasePackageIndexBackend
from populus.packages.backends.manifest import LocalManifestBackend
from populus.packages.backends.lockfile import LocalFilesystemLockfileBackend

from populus.utils.filesystem import (
    find_solidity_source_files,
    is_same_path,
)
from populus.utils.dependencies import (
    get_dependency_base_dir,
    get_build_identifier,
    get_install_identifier,
    get_release_lockfile_path,
    get_installed_packages_dir,
)
from populus.utils.ipfs import (
    is_ipfs_uri,
    generate_file_hash,
    extract_ipfs_path_from_uri,
)
from populus.utils.packaging import (
    is_aliased_ipfs_uri,
    load_release_lockfile,
)


class MockPackageIndexBackend(BasePackageIndexBackend):
    packages = None

    def setup_backend(self):
        self.packages = {}

    def publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        package_name = release_lockfile['package_name']
        self.packages.setdefault(package_name, {})
        if release_lockfile['version'] in self.packages[package_name]:
            raise ValueError("Cannot overwrite release")
        self.packages[package_name][release_lockfile['version']] = release_lockfile_uri

    def is_known_package_name(self, package_name):
        return package_name in self.packages

    def get_all_versions(self, package_name):
        return (self.packages[package_name].keys())

    def get_release_lockfile_for_version(self, package_name, version):
        return self.packages[package_name][version]


class MockIPFSBackend(BaseIPFSPackageBackend):
    files = None

    def setup_backend(self):
        self.files = {}

    @to_dict
    def resolve_package_source_tree(self, release_lockfile):
        sources = release_lockfile['sources']

        for source_path, source_value in sources.items():
            if is_ipfs_uri(source_value):
                ipfs_path = extract_ipfs_path_from_uri(source_value)
                yield source_path, self.files[ipfs_path]
            else:
                yield source_path, source_value

    def push_file_to_ipfs(self, file_path):
        ipfs_hash = generate_file_hash(file_path)
        with open(file_path) as file:
            file_contents = file.read()
            self.files[ipfs_hash] = file_contents
        return ipfs_hash

    def get_file_from_ipfs(self, ipfs_path):
        file_contents = self.files[ipfs_path]
        return file_contents


@pytest.fixture()
def mock_package_index_backend(project):
    return MockPackageIndexBackend(project, {})


@pytest.fixture()
def mock_IPFS_backend(project):
    return MockIPFSBackend(project, {})


@pytest.fixture()
def mock_package_backends(project, mock_IPFS_backend, mock_package_index_backend):
    package_backends = OrderedDict((
        ('LocalManifestBackend', LocalManifestBackend(project, {})),
        ('LocalFilesystemLockfileBackend', LocalFilesystemLockfileBackend(project, {})),
        ('MockIPFSBackend', mock_IPFS_backend),
        ('MockPackageIndexBackend', mock_package_index_backend),
    ))
    return package_backends


EXAMPLE_PACKAGES_BASE_PATH = './tests/example-packages'


@pytest.fixture()
def load_example_project(populus_source_root,
                         mock_package_index_backend,
                         mock_IPFS_backend):
    def _load_example_project(project_name):
        project_base_dir = os.path.join(
            populus_source_root,
            EXAMPLE_PACKAGES_BASE_PATH,
            project_name,
        )
        v1_release_lockfile_path = os.path.join(project_base_dir, '1.0.0.json')
        contracts_source_dir = os.path.join(project_base_dir, 'contracts')

        v1_release_lockfile_uri = mock_IPFS_backend.persist_package_file(
            v1_release_lockfile_path,
        )
        v1_release_lockfile = load_release_lockfile(v1_release_lockfile_path)
        mock_package_index_backend.publish_release_lockfile(
            v1_release_lockfile,
            v1_release_lockfile_uri,
        )

        for solidity_source_path in find_solidity_source_files(contracts_source_dir):
            mock_IPFS_backend.persist_package_file(solidity_source_path)
    return _load_example_project


@pytest.fixture()
def verify_installed_package():
    def _verify_installed_package(installed_packages_dir, package_base_dir, package_data):
        package_meta = package_data['meta']

        expected_package_base_dir = get_dependency_base_dir(
            installed_packages_dir,
            package_meta['dependency_name'],
        )

        assert os.path.exists(package_base_dir)
        assert is_same_path(package_base_dir, expected_package_base_dir)

        for rel_source_path, source_contents in package_data['source_tree'].items():
            source_path = os.path.join(package_base_dir, rel_source_path)
            assert os.path.exists(source_path)
            with open(source_path) as source_file:
                actual_source_contents = source_file.read()
            assert actual_source_contents == source_contents

        build_identifier = get_build_identifier(package_base_dir)
        assert build_identifier == package_meta['build_identifier']

        install_identifier = get_install_identifier(package_base_dir)
        assert install_identifier == package_meta['install_identifier']

        release_lockfile_path = get_release_lockfile_path(package_base_dir)
        release_lockfile = load_release_lockfile(release_lockfile_path)

        assert release_lockfile == package_data['lockfile']

        package_installed_packages_dir = get_installed_packages_dir(package_base_dir)

        for dependency_package_data in package_data['dependencies']:
            sub_dependency_base_dir = get_dependency_base_dir(
                package_installed_packages_dir,
                dependency_package_data['meta']['dependency_name'],
            )
            _verify_installed_package(
                package_installed_packages_dir,
                sub_dependency_base_dir,
                dependency_package_data,
            )
    return _verify_installed_package
