import json

import ipfsapi

from eth_utils import (
    force_text,
    to_dict,
)

from populus.utils.packaging import (
    is_aliased_ipfs_uri,
)
from populus.utils.ipfs import (
    is_ipfs_uri,
    create_ipfs_uri,
    extract_ipfs_path_from_uri,
    walk_ipfs_tree,
)

from .base import (
    BasePackageBackend,
)


class BaseIPFSPackageBackend(BasePackageBackend):
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
        lockfile_contents = self.get_file_from_ipfs(ipfs_path)
        release_lockfile = json.loads(force_text(lockfile_contents))
        return release_lockfile

    def can_resolve_package_source_tree(self, release_lockfile):
        sources = release_lockfile.get('sources')
        if sources is None:
            return False
        return all(
            is_ipfs_uri(value) for value in sources.values()
        )

    def can_persist_package_file(self, file_path):
        return True

    def persist_package_file(self, file_path):
        """
        Persists the provided file to this backends persistence layer.
        """
        ipfs_file_hash = self.push_file_to_ipfs(file_path)
        ipfs_uri = create_ipfs_uri(ipfs_file_hash)
        return ipfs_uri

    #
    # Subclass API
    #
    def push_file_to_ipfs(self, file_path):
        raise NotImplementedError("Must be implemented by subclasses")

    def get_file_from_ipfs(self, ipfs_path):
        raise NotImplementedError("Must be implemented by subclasses")


class IPFSPackageBackend(BaseIPFSPackageBackend):
    """
    Package backend that resolves IPFS URIs
    """
    def setup_backend(self):
        ipfs_host = self.settings['host']
        ipfs_port = self.settings['port']
        self.ipfs_client = ipfsapi.connect(ipfs_host, ipfs_port)

    @to_dict
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

    def push_file_to_ipfs(self, file_path):
        """
        Persists the provided file to this backends persistence layer.
        """
        result = self.ipfs_client.add(file_path)
        ipfs_file_hash = result['Hash']
        return ipfs_file_hash

    def get_file_from_ipfs(self, ipfs_path):
        file_contents = self.ipfs_client.cat(ipfs_path)
        return file_contents
