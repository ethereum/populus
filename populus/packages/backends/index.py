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
    def find_best_version_match(self, package_name, comparison, version):
        if comparison is None and version is None:
            return self.get_latest_release_lockfile(package_name)
        if comparison is None:
            raise ValueError("Invariant")
        if version is None:
            raise ValueError("Invariant")

        all_release_data = self.get_all_release_data(package_name)
        matching_versions = filter_versions(comparison, version, all_release_data.keys())
        best_match = get_max_version(matching_versions)

        return best_match

    def lookup_release_lockfile_uri(self, package_name, version):
        all_release_data = self.get_all_release_data(package_name)
        return all_release_data[version]

    def get_latest_release(self, package_name):
        major, minor, patch, release_lockfile_uri = self.call().latestVersion(
            package_name,
        )
        if major == 0 and minor == 0 and patch == 0:
            raise ValueError("Invalid version number. 0.0.0 is not allowed")
        if not release_lockfile_uri:
            raise ValueError("No lockfile URI")
        version = '.'.join((str(major), str(minor), str(patch)))
        return version, release_lockfile_uri

    def get_latest_release_version(self, package_name):
        return self.get_latest_release(package_name)[0]

    def get_latest_release_lockfile(self, package_name):
        return self.get_latest_release(package_name)[1]

    def get_all_release_data(self, package_name):
        all_releases_raw = tuple((
            self.call().getRelease(package_name, idx)
            for idx in range(self.get_num_releases(package_name))
        ))
        all_release_data = {
            "{0}.{1}.{2}".format(major, minor, patch): lockfile_uri
            for major, minor, patch, lockfile_uri
            in all_releases_raw
        }
        return all_release_data

    def is_known_package_name(self, package_name):
        return self.call().exists(package_name)

    def get_num_releases(self, package_name):
        return self.call().numReleases(package_name)

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


class PackageIndexBackend(BasePackageBackend):
    package_index = None

    def setup_backend(self):
        package_index_address = self.settings['package_index_address']
        PackageIndexFactory = self.get_package_index_factory()
        self.package_index = PackageIndexFactory(address=package_index_address)

    def can_translate_package_identifier(self, package_identifier):
        is_named_package_identifier = any((
            is_direct_package_identifier(package_identifier),
            is_aliased_package_identifier(package_identifier),
        ))

        if not is_named_package_identifier:
            return False

        package_name, _, _ = parse_package_identifier(package_identifier)
        return self.package_index.is_known_package_name(package_name)

    def translate_package_identifier(self, package_identifier):
        if is_package_name(package_identifier):
            latest_version = self.package_index.get_latest_release_version(package_identifier)
            return (
                '=='.join((package_identifier, latest_version)),
            )
        elif is_aliased_package_name(package_identifier):
            _, _, package_name = package_identifier.partition(':')
            return (
                package_name,
            )
        else:
            package_name, comparison, version = parse_package_identifier(package_identifier)
            best_match = self.package_index.find_best_version_match(package_identifier),

            if comparison == '==':
                return (
                    self.package_index.lookup_release_lockfile_uri(best_match),
                )
            else:
                return (
                    '=='.join((package_name, best_match)),
                )

    def can_publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        return True

    def publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        publish_txn_hash = self.package_index.publish_release(
            release_lockfile['package_name'],
            release_lockfile['version'],
            release_lockfile_uri,
        )
        return publish_txn_hash

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
