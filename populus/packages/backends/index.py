import os
import json

import semver

from web3.contract import Contract

from populus import ASSETS_DIR

from populus.utils.chains import (
    setup_web3_from_config,
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
        return self.call().getReleaseLockFile(
            name=package_name,
            major=version_info.major,
            minor=version_info.minor,
            patch=version_info.patch,
        )

    def get_all_versions(self, package_name):
        return tuple(self.get_all_release_data(package_name).keys())
        all_version_info = tuple((
            self.call().getRelease(package_name, idx)
            for idx in range(self.call().numReleases(package_name))
        ))
        all_versions = tuple((
            "{0}.{1}.{2}".format(major, minor, patch)
            for major, minor, patch, _
            in all_version_info
        ))
        return all_versions

    def is_known_package_name(self, package_name):
        return self.call().exists(package_name)

    def publish_release(self, package_name, version, release_lockfile_uri, transaction=None):
        version_info = semver.parse_version_info(version)
        major, minor, patch = version_info.major, version_info.minor, version_info.patch
        publish_txn_hash = self.transact(transaction).release(
            name=package_name,
            major=major,
            minor=minor,
            patch=patch,
            releaseLockFileURI=release_lockfile_uri,
        )
        return publish_txn_hash


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
    package_index = None

    def setup_backend(self):
        package_index_address = self.settings['package_index_address']
        PackageIndexFactory = self.get_package_index_factory()
        self.package_index = PackageIndexFactory(address=package_index_address)

    def publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        publish_txn_hash = self.package_index.publish_release(
            release_lockfile['package_name'],
            release_lockfile['version'],
            release_lockfile_uri,
        )
        return publish_txn_hash

    def is_known_package_name(self, package_name):
        return self.package_index.is_known_package_name(package_name)

    def get_all_versions(self, package_name):
        return self.package_index.get_all_versions(package_name)

    def get_release_lockfile_for_version(self, package_name, version):
        return self.package_index.lookup_release_lockfile_uri(package_name, version)

    #
    # Internal API
    #
    def get_web3(self):
        web3_config = self.settings.get_config('web3')
        web3 = setup_web3_from_config(web3_config)
        return web3

    def get_package_index_factory(self):
        with open(PACKAGE_INDEX_ABI_PATH) as package_index_abi_file:
            package_index_abi = json.load(package_index_abi_file)

        web3 = self.get_web3()

        return web3.eth.contract(
            abi=package_index_abi,
            base_contract_factory_class=BasePackageIndexFactory,
        )
