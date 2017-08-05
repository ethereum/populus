import os
import json

import semver

from web3.contract import Contract

from populus import ASSETS_DIR

from populus.config import (
    Web3Config,
)
from populus.utils.packaging import (
    is_direct_package_identifier,
    is_aliased_package_identifier,
    parse_package_identifier,
    filter_versions,
    get_max_version,
    is_package_name,
    is_aliased_package_name,
)
from .base import (
    BasePackageBackend,
)


PACKAGE_INDEX_ABI_PATH = os.path.join(ASSETS_DIR, 'package_index_abi.json')


class BasePackageIndexFactory(Contract):
    def lookup_release_lockfile_uri(self, package_name, version):
        version_info = semver.parse_version_info(version)
        return self.call().getReleaseLockfileURI(
            name=package_name,
            major=version_info.major,
            minor=version_info.minor,
            patch=version_info.patch,
            preRelease=version_info.prerelease or '',
            build=version_info.build or '',
        )

    def get_all_versions(self, package_name):
        all_release_hashes = self.call().getAllPackageReleaseHashes(package_name)
        all_release_data = tuple((
            self.call().getReleaseData(release_hash)
            for release_hash in all_release_hashes
        ))
        all_versions = tuple((
            semver.format_version(major, minor, patch, prerelease or None, build or None)
            for major, minor, patch, prerelease, build, _, _, _
            in all_release_data
        ))
        return all_versions

    def is_known_package_name(self, package_name):
        return self.call().packageExists(package_name)

    def release(self, package_name, version, release_lockfile_uri, transaction=None):
        version_info = semver.parse_version_info(version)
        release_txn_hash = self.transact(transaction).release(
            name=package_name,
            major=version_info.major,
            minor=version_info.minor,
            patch=version_info.patch,
            preRelease=version_info.prerelease or '',
            build=version_info.build or '',
            releaseLockfileURI=release_lockfile_uri,
        )
        return release_txn_hash


class BasePackageIndexBackend(BasePackageBackend):
    def can_translate_package_identifier(self, package_identifier):
        is_named_package_identifier = any((
            is_direct_package_identifier(package_identifier),
            is_aliased_package_identifier(package_identifier),
        ))

        if not is_named_package_identifier:
            return False

        package_name, _, _ = parse_package_identifier(package_identifier)
        return self.is_known_package_name(package_name)

    def translate_package_identifier(self, package_identifier):
        if is_package_name(package_identifier):
            latest_version = self.get_latest_version(package_identifier)
            return (
                '=='.join((package_identifier, latest_version)),
            )
        elif is_aliased_package_name(package_identifier):
            _, _, package_name = package_identifier.partition(':')
            return (
                package_name,
            )
        else:
            latest_matching_version = self.get_latest_matching_version(package_identifier)
            package_name, comparison, _ = parse_package_identifier(package_identifier)

            if comparison == '==':
                return (
                    self.get_release_lockfile_for_version(package_name, latest_matching_version),
                )
            else:
                return (
                    '=='.join((package_name, latest_matching_version)),
                )

    def can_publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        return True

    def get_latest_version(self, package_name):
        all_versions = self.get_all_versions(package_name)
        return get_max_version(all_versions)

    def get_latest_matching_version(self, package_identifier):
        package_name, comparison, version = parse_package_identifier(package_identifier)

        if comparison is None and version is None:
            return self.get_latest_version(package_name)
        if comparison is None:
            raise ValueError("Invariant")
        if version is None:
            raise ValueError("Invariant")

        all_versions = self.get_all_versions(package_name)
        matching_versions = filter_versions(comparison, version, all_versions)
        latest_matching_version = get_max_version(matching_versions)

        return latest_matching_version

    #
    # Overide these API methods
    #
    def publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        raise NotImplementedError("Must be implemented by subclasses")

    def get_all_versions(self, package_name):
        raise NotImplementedError("Must be implemented by subclasses")

    def is_known_package_name(self, package_name):
        raise NotImplementedError("Must be implemented by subclasses")

    def get_release_lockfile_for_version(self, package_name, version):
        raise NotImplementedError("Must be implemented by subclasses")


class PackageIndexBackend(BasePackageIndexBackend):
    package_index_for_install = None
    package_index_for_publish = None

    def setup_backend(self):
        if 'web3-for-install' in self.settings:
            self.package_index_for_install = self.get_package_index_for_install()
        if 'web3-for-publish' in self.settings:
            self.package_index_for_publish = self.get_package_index_for_publish()

    def can_translate_package_identifier(self, package_identifier):
        return 'web3-for-install' in self.settings

    def can_publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        return 'web3-for-publish' in self.settings

    def publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        publish_txn_hash = self.package_index_for_publish.release(
            release_lockfile['package_name'],
            release_lockfile['version'],
            release_lockfile_uri,
        )
        return publish_txn_hash

    def is_known_package_name(self, package_name):
        return self.package_index_for_install.is_known_package_name(package_name)

    def get_all_versions(self, package_name):
        return self.package_index_for_install.get_all_versions(package_name)

    def get_release_lockfile_for_version(self, package_name, version):
        return self.package_index_for_install.lookup_release_lockfile_uri(package_name, version)

    #
    # Internal API
    #
    def get_web3_for_install(self):
        web3_config = self.settings.get_config('web3-for-install', config_class=Web3Config)
        web3 = web3_config.get_web3()
        return web3

    def get_package_index_for_install(self):
        PackageIndexFactory = self.get_package_index_factory(self.get_web3_for_install())
        package_index_address = self.settings['package_index_address']
        return PackageIndexFactory(address=package_index_address)

    def get_web3_for_publish(self):
        web3_config = self.settings.get_config('web3-for-publish', config_class=Web3Config)
        web3 = web3_config.get_web3()
        return web3

    def get_package_index_for_publish(self):
        PackageIndexFactory = self.get_package_index_factory(self.get_web3_for_publish())
        package_index_address = self.settings['package_index_address']
        return PackageIndexFactory(address=package_index_address)

    def get_package_index_factory(self, web3):
        with open(PACKAGE_INDEX_ABI_PATH) as package_index_abi_file:
            package_index_abi = json.load(package_index_abi_file)

        return web3.eth.contract(
            abi=package_index_abi,
            ContractFactoryClass=BasePackageIndexFactory,
        )
