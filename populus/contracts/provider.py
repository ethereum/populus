from pylru import lrucache

from populus.utils.contracts import (
    get_shallow_dependency_graph,
    get_recursive_contract_dependencies,
    verify_contract_bytecode,
)
from populus.utils.deploy import (
    compute_deploy_order,
)
from populus.utils.linking import (
    find_link_references,
)

from .exceptions import (
    NoKnownAddress,
    BytecodeMismatch,
)


class Provider(object):
    """
    Abstraction for retrieving contracts on a given chain.
    """
    provider_backends = None

    def __init__(self, chain, provider_backends):
        self.chain = chain
        self.provider_backends = provider_backends
        self._factory_cache = lrucache(128)

    def is_contract_available(self, contract_identifier):
        try:
            contract_address = self.get_contract_address(contract_identifier)
        except NoKnownAddress:
            return False

        BaseContractFactory = self.chain.store.get_base_contract_factory(contract_identifier)

        all_dependencies_are_available = all(
            self.is_contract_available(link_reference.full_name)
            for link_reference
            in find_link_references(
                BaseContractFactory.bytecode,
                set(self.chain.project.compiled_contract_data.keys())
            )
        )
        if not all_dependencies_are_available:
            return False

        ContractFactory = self.chain.store.get_contract_factory(contract_identifier)
        try:
            verify_contract_bytecode(self.chain.web3, ContractFactory, contract_address)
        except (BytecodeMismatch, ValueError):
            return False

        return True

    def are_contract_dependencies_available(self, contract_identifier):
        full_dependency_graph = get_shallow_dependency_graph(
            self.chain.project.compiled_contract_data,
        )
        contract_dependencies = get_recursive_contract_dependencies(
            contract_identifier,
            full_dependency_graph,
        )

        dependency_deploy_order = [
            dependency_name
            for dependency_name
            in compute_deploy_order(full_dependency_graph)
            if dependency_name in contract_dependencies
        ]
        for dependency_name in dependency_deploy_order:
            if self.is_contract_available(dependency_name):
                continue
            return False
        else:
            return True

    def get_contract(self, contract_identifier):
        ContractFactory = self.chain.store.get_contract_factory(contract_identifier)
        contract_address = self.get_contract_address(contract_identifier)

        verify_contract_bytecode(self.chain.web3, ContractFactory, contract_address)

        return ContractFactory(address=contract_address)

    def deploy_contract(self,
                        contract_identifier,
                        deploy_transaction=None,
                        deploy_args=None,
                        deploy_kwargs=None):
        """
        Same as get_contract but it will also lazily deploy the contract with
        the provided deployment arguments
        """
        full_dependency_graph = get_shallow_dependency_graph(
            self.chain.project.compiled_contract_data,
        )
        contract_dependencies = get_recursive_contract_dependencies(
            contract_identifier,
            full_dependency_graph,
        )

        dependency_deploy_order = [
            dependency_name
            for dependency_name
            in compute_deploy_order(full_dependency_graph)
            if dependency_name in contract_dependencies
        ]
        for dependency_name in dependency_deploy_order:
            self.get_or_deploy_contract(dependency_name)

        ContractFactory = self.chain.store.get_contract_factory(contract_identifier)
        deploy_transaction_hash = ContractFactory.deploy(
            transaction=deploy_transaction,
            args=deploy_args,
            kwargs=deploy_kwargs,
        )
        contract_address = self.chain.wait.for_contract_address(deploy_transaction_hash)
        registrar = self.chain.registrar
        registrar.set_contract_address(contract_identifier, contract_address)

        return self.get_contract(contract_identifier), deploy_transaction_hash

    def get_or_deploy_contract(self,
                               contract_identifier,
                               deploy_transaction=None,
                               deploy_args=None,
                               deploy_kwargs=None):
        """
        Same as get_contract but it will also lazily deploy the contract with
        the provided deployment arguments
        """
        if not self.is_contract_available(contract_identifier):
            return self.deploy_contract(
                contract_identifier=contract_identifier,
                deploy_transaction=deploy_transaction,
                deploy_args=deploy_args,
                deploy_kwargs=deploy_kwargs,
            )
        else:
            return (
                self.get_contract(contract_identifier),
                None,
            )

    def get_contract_address(self, contract_identifier):
        """
        Retrieve a contract address from the provider backends.
        """
        # TODO: this should really evaluate *all* addresses returned and then
        # figure out if any of them are the correct addresses.
        for provider in self.provider_backends.values():
            try:
                return provider.get_contract_address(contract_identifier)
            except NoKnownAddress:
                continue
        else:
            raise NoKnownAddress("No known address for contract")
