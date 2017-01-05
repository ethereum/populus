import pytest

from populus.utils.packaging import (
    is_direct_package_identifier,
    is_aliased_package_identifier,
    filter_versions,
    get_max_version,
    parse_package_identifier,
    is_aliased_ipfs_uri,
)
from populus.utils.ipfs import (
    generate_ipfs_file_multihash,
)

from populus.packages.backends.base import BasePackageBackend


class MockPackageIndexBackend(BasePackageBackend):
    packages = None

    def setup_backend(self):
        self.packages = {}

    def can_translate_package_identifier(self, package_identifier):
        """
        Returns `True` or `False` as to whether this backend is capable of
        translating this identifier.
        """
        is_named_package_identifier = any((
            is_direct_package_identifier(package_identifier),
            is_aliased_package_identifier(package_identifier),
        ))

        if not is_named_package_identifier:
            return False

        package_name, _, _ = parse_package_identifier(package_identifier)
        return package_name in self.packages

    def translate_package_identifier(self, package_identifier):
        if is_package_name(package_identifier):
            latest_version = self.package_index.get_latest_release_version(package_identifier)
            return (
                '=='.join((package_identifier, latest_version)),
            )
        else:
            package_name, comparison, version = parse_package_identifier(
                package_identifier,
            )
            all_release_data = self.packages[package_name]
            matching_versions = filter_versions(comparison, version, all_release_data.keys())
            best_match = get_max_version(matching_versions)

            return (
                all_release_data[best_match],
            )

    def can_publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        return True

    def publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        package_name = release_lockfile['package_name']
        self.packages.setdefault(package_name, {})
        if release_lockfile['version'] in self.packages[package_name]:
            raise ValueError("Cannot overwrite release")
        self.packages[package_name][release_lockfile['version']] = release_lockfile_uri


class MockIPFSBackend(BasePackageBackend):
    files = None

    def setup_backend(self):
        files = {}

    def can_translate_package_identifier(self, package_identifier):
        return is_aliased_ipfs_uri(package_identifier)

    def translate_package_identifier(self, package_identifier):
        _, _, ipfs_uri = package_identifier.partition('@')
        return (
            ipfs_uri,
        )

    def can_resolve_to_release_lockfile(self, package_identifier):
        if is_ipfs_uri(package_identifier):
            return True
        return False

    def resolve_to_release_lockfile(self, package_identifier):
        ipfs_path = extract_ipfs_path_from_uri(package_identifier)
        lockfile_contents = self.files[ipfs_path]
        release_lockfile = json.loads(lockfile_contents)
        return release_lockfile

    def can_resolve_package_source_tree(self, release_lockfile):
        sources = release_lockfile.get('sources')
        if sources is None:
            return False
        return all(
            is_ipfs_uri(value) for value in sources.values()
        )

    @cast_return_to_dict
    def resolve_package_source_tree(self, release_lockfile):
        sources = release_lockfile['sources']

        for source_path, source_value in sources.items():
            if is_ipfs_uri(source_value):
                ipfs_path = extract_ipfs_path_from_uri(source_value)
                ipfs_source_tree = walk_ipfs_tree(self.ipfs_client, ipfs_path, source_path)
                for sub_path, source_hash in ipfs_source_tree.items():
                    source_content = self.ipfs_client.cat(source_hash)
                    yield sub_path, source_content
            else:
                yield source_path, source_value

    #
    # Write API primarily for publishing
    #
    def can_persist_package_file(self, file_path):
        return True

    def persist_package_file(self, file_path):
        """
        Persists the provided file to this backends persistence layer.
        """
        result = self.ipfs_client.add(file_path)
        ipfs_file_hash = result['Hash']
        ipfs_uri = create_ipfs_uri(ipfs_file_hash)
        return ipfs_uri
