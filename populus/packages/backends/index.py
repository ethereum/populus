import os
import json

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
)
from .base import (
    BasePackageBackend,
)


PACKAGE_INDEX_ABI_PATH = os.path.join(ASSETS_DIR, 'package_index_abi.json')


class BasePackageIndexFactory(Contract):
    def lookup_release_lockfile_uri(self, package_identifier):
        package_name, comparison, version = parse_package_identifier(package_identifier)

        if comparison is None and version is None:
            return self.get_latest_release(package_name)
        if comparison is None:
            raise ValueError("Invariant")
        if version is None:
            raise ValueError("Invariant")

        all_release_data = self.get_all_release_data(package_name)
        matching_versions = filter_versions(comparison, version, all_release_data.keys())
        best_match = get_max_version(matching_versions)

        return all_release_data[best_match]

    def get_latest_release(self, package_name):
        major, minor, patch, release_lockfile_uri = self.call().latest(
            package_name,
        )
        if major == 0 and minor == 0 and patch == 0:
            raise ValueError("Invalid version number. 0.0.0 is not allowed")
        if not release_lockfile_uri:
            raise ValueError("No lockfile URI")
        return release_lockfile_uri

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


class PackageIndexBackend(BasePackageBackend):
    package_index = None

    def __init__(self, project, settings):
        super(PackageIndexBackend, self).__init__(project, settings)
        self.setup_package_index()

    def can_translate_package_identifier(self, package_identifier):
        return any((
            is_direct_package_identifier(package_identifier),
            is_aliased_package_identifier(package_identifier),
        ))

    def translate_package_identifier(self, package_identifier):
        if is_direct_package_identifier(package_identifier):
            package_name, _, _ = parse_package_identifier(package_identifier)
            return (
                self.package_index.is_known_package_name(package_name),
            )
        elif is_aliased_package_identifier(package_identifier):
            dependency_name, _, sub_package_identifier = package_identifier.partition(':')
            package_name, _, _ = parse_package_identifier(sub_package_identifier)
            return (
                self.package_index.is_known_package_name(package_name),
            )
        else:
            raise ValueError("Unsupported Identifier: '{0}'".format(package_identifier))

    def can_publish_release_lockfile(self, release_lockfile):
        return True

    def publish_release_lockfile(self, release_lockfile):
        assert False

    #
    # Internal API
    #
    def get_web3(self):
        web3_config = self.settings.get_config('web3')
        if '$ref' in web3_config:
            web3_config = self.project.config.get(web3_config['$ref'])
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

    def setup_package_index(self):
        package_index_address = self.settings['package_index_address']
        PackageIndexFactory = self.get_package_index_factory()
        self.package_index = PackageIndexFactory(address=package_index_address)
