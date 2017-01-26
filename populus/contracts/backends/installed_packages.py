from populus.contracts.exceptions import NoKnownAddress

from populus.utils.chains import (
    check_if_chain_matches_chain_uri,
)
from populus.utils.packaging import (
    get_release_lockfile_path,
    get_installed_dependency_locations,
    load_release_lockfile,
)

from .base import BaseContractBackend


def get_deployed_contract_instances_from_installed_packages(web3,
                                                            installed_packages_dir,
                                                            contract_name):
    installed_dependency_locations = get_installed_dependency_locations(installed_packages_dir)
    for package_base_dir in installed_dependency_locations.values():
        release_lockfile_path = get_release_lockfile_path(package_base_dir)
        release_lockfile = load_release_lockfile(release_lockfile_path)

        deployments = release_lockfile.get('deployments', {})
        for chain_uri, deployed_contract_instances in deployments.items():
            if not check_if_chain_matches_chain_uri(web3, chain_uri):
                continue
            if contract_name in deployed_contract_instances:
                return deployed_contract_instances[contract_name]['address']
    raise NoKnownAddress("No known address for '{0}'".format(contract_name))


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
        return get_deployed_contract_instances_from_installed_packages(
            web3,
            self.chain.project.installed_packages_dir,
            contract_name,
        )
