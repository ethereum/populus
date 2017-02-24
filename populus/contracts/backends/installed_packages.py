from eth_utils import (
    compose,
    to_tuple,
)

from populus.contracts.exceptions import (
    NoKnownAddress,
)

from populus.utils.chains import (
    check_if_chain_matches_chain_uri,
)
from populus.utils.contracts import (
    is_dependency_contract,
    is_dependency_contract_name,
    map_contracts_to_source_location,
)
from populus.utils.dependencies import (
    build_dependency_namespace_lookups,
    recursive_find_installed_dependency_base_dirs,
    get_release_lockfile_path,
)
from populus.utils.functional import (
    cached_property,
    to_set,
)
from populus.utils.packaging import (
    load_release_lockfile,
)

from .base import BaseContractBackend


@to_tuple
def get_deployed_contract_instances_from_installed_packages(web3,
                                                            installed_packages_dir,
                                                            instance_name):
    installed_dependency_locations = recursive_find_installed_dependency_base_dirs(
        installed_packages_dir,
    )
    for package_base_dir in installed_dependency_locations:
        release_lockfile_path = get_release_lockfile_path(package_base_dir)
        release_lockfile = load_release_lockfile(release_lockfile_path)

        deployments = release_lockfile.get('deployments', {})
        for chain_uri, deployed_contract_instances in deployments.items():
            if not check_if_chain_matches_chain_uri(web3, chain_uri):
                continue
            if instance_name in deployed_contract_instances:
                yield deployed_contract_instances[instance_name]


class InstalledPackagesBackend(BaseContractBackend):
    """
    A contract backend that only acts as a provider sourcing contracts from
    installed packages.
    """
    is_registrar = True
    is_provider = True
    is_store = True

    #
    # Registrar API
    #
    def get_contract_addresses(self, instance_name):
        web3 = self.chain.web3
        deployed_instances = get_deployed_contract_instances_from_installed_packages(
            web3,
            self.chain.project.installed_packages_dir,
            instance_name,
        )
        if not deployed_instances:
            raise NoKnownAddress("No deployed instances of {0} found".format(instance_name))
        return tuple(
            deployed_instance['address'] for deployed_instance in deployed_instances
        )

    def set_contract_address(self, *args, **kwargs):
        pass

    #
    # Provider API
    #
    def get_contract_identifier(self, contract_name):
        if is_dependency_contract_name(contract_name):
            return contract_name
        contract_name_to_dependency_namespace = compose(
            self.dependencies_contract_data_source_path_lookup.__getitem__,
            self.dependencies_namespace_lookup.__getitem__,
        )
        return ":".join((
            contract_name_to_dependency_namespace(contract_name),
            contract_name,
        ))

    def get_all_contract_data(self):
        namespaced_dependencies_contract_data = {
            self.get_contract_identifier(contract_name): contract_data
            for contract_name, contract_data
            in self.dependencies_contract_data.items()
        }
        return namespaced_dependencies_contract_data

    @to_set
    def get_all_contract_names(self):
        for contract_identifier in self.get_all_contract_data().keys():
            _, _, contract_name = contract_identifier.rpartition(':')
            yield contract_name

    #
    # Private API
    #
    @cached_property
    def all_dependency_base_dirs(self):
        return recursive_find_installed_dependency_base_dirs(
            self.chain.project.installed_packages_dir,
        )

    @cached_property
    def dependencies_contract_data(self):
        return {
            contract_name: contract_data
            for contract_name, contract_data
            in self.chain.project.compiled_contract_data.items()
            if is_dependency_contract(self.chain.project.installed_packages_dir, contract_data)
        }

    @cached_property
    def dependencies_contract_data_source_path_lookup(self):
        return map_contracts_to_source_location(
            self.dependencies_contract_data,
            self.all_dependency_base_dirs,
        )

    @cached_property
    def dependencies_namespace_lookup(self):
        return build_dependency_namespace_lookups(
            self.all_dependency_base_dirs,
        )
