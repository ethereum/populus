import pytest

import os
import json
from collections import OrderedDict

from populus import Project

from populus.utils.packaging import (
    is_aliased_ipfs_uri,
)
from populus.utils.functional import (
    cast_return_to_dict,
)
from populus.utils.filesystem import (
    find_solidity_source_files,
)
from populus.utils.ipfs import (
    is_ipfs_uri,
    generate_file_hash,
    create_ipfs_uri,
    extract_ipfs_path_from_uri,
)

from populus.packages.backends.ipfs import BaseIPFSPackageBackend
from populus.packages.backends.index import BasePackageIndexBackend
from populus.packages.backends.manifest import LocalManifestBackend
from populus.packages.backends.lockfile import LocalFilesystemLockfileBackend


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

    def resolve_to_release_lockfile(self, package_identifier):
        ipfs_path = extract_ipfs_path_from_uri(package_identifier)
        lockfile_contents = self.files[ipfs_path]
        release_lockfile = json.loads(lockfile_contents)
        return release_lockfile

    @cast_return_to_dict
    def resolve_package_source_tree(self, release_lockfile):
        sources = release_lockfile['sources']

        for source_path, source_value in sources.items():
            if is_ipfs_uri(source_value):
                ipfs_path = extract_ipfs_path_from_uri(source_value)
                yield source_path, self.files[ipfs_path]
            else:
                yield source_path, source_value

    def persist_package_file(self, file_path):
        """
        Persists the provided file to this backends persistence layer.
        """
        ipfs_hash = generate_file_hash(file_path)
        with open(file_path) as file:
            file_contents = file.read()
            self.files[ipfs_hash] = file_contents
        ipfs_uri = create_ipfs_uri(ipfs_hash)
        return ipfs_uri


@pytest.fixture()
def project(project_dir):
    _project = Project()
    return _project


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
        with open(v1_release_lockfile_path) as v1_release_lockfile_file:
            v1_release_lockfile = json.load(v1_release_lockfile_file)
            mock_package_index_backend.publish_release_lockfile(
                v1_release_lockfile,
                v1_release_lockfile_uri,
            )

        for solidity_source_path in find_solidity_source_files(contracts_source_dir):
            mock_IPFS_backend.persist_package_file(solidity_source_path)
    return _load_example_project
