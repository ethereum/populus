import json

from populus.contracts.exceptions import NoKnownAddress

from populus.utils.chains import (
    check_if_chain_matches_chain_uri,
)
from populus.utils.packaging import (
    get_release_lockfile_path,
)

from .base import BaseContractBackend


class InstalledPackagesContractBackend(BaseContractBackend):
    """
    A contract backend that only acts as a provider sourcing contracts from
    installed packages.
    """
    def is_registrar(self):
        return False

    def is_provider(self):
        return True

    def get_contract_address(self, contract_name):
        web3 = self.chain.web3

        for package_base_dir in self.chain.project.installed_package_locations.values():
            release_lockfile_path = get_release_lockfile_path(package_base_dir)
            with open(release_lockfile_path) as release_lockfile_file:
                release_lockfile = json.load(release_lockfile_file)

            deployments = release_lockfile.get('deployments', {})
            for chain_uri, deployed_contract_instances in deployments.items():
                if not check_if_chain_matches_chain_uri(web3, chain_uri):
                    continue
                if contract_name in deployed_contract_instances:
                    return deployed_contract_instances[contract_name]['address']
        raise NoKnownAddress("No known address for '{0}'".format(contract_name))
