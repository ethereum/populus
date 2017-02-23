from pylru import lrucache

from populus.utils.contracts import (
    package_contracts,
    get_shallow_dependency_graph,
    get_recursive_contract_dependencies,
    verify_contract_bytecode,
)
from populus.utils.deploy import (
    compute_deploy_order,
)
from populus.utils.linking import (
    link_bytecode,
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

    def get_contract_factory(self, contract_identifier):
        if contract_identifier in self._factory_cache:
            return self._factory_cache[contract_identifier]

        BaseContractFactory = self.chain.store.get_base_contract_factory(contract_identifier)

        bytecode = self.link_bytecode(BaseContractFactory.bytecode)
        bytecode_runtime = self.link_bytecode(BaseContractFactory.bytecode_runtime)

        ContractFactory = BaseContractFactory.factory(
            web3=BaseContractFactory.web3,
            bytecode=bytecode,
            bytecode_runtime=bytecode_runtime,
        )

        self._factory_cache[contract_identifier] = ContractFactory
        return ContractFactory

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

        ContractFactory = self.get_contract_factory(contract_identifier)
        try:
            verify_contract_bytecode(self.chain.web3, ContractFactory, contract_address)
        except (BytecodeMismatch, ValueError):
            return False

        return True

    def are_contract_factory_dependencies_available(self, contract_identifier):
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
        ContractFactory = self.get_contract_factory(contract_identifier)
        contract_address = self.get_contract_address(contract_identifier)

        verify_contract_bytecode(self.chain.web3, ContractFactory, contract_address)

        return ContractFactory(address=contract_address)

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

            ContractFactory = self.get_contract_factory(contract_identifier)
            deploy_transaction_hash = ContractFactory.deploy(
                transaction=deploy_transaction,
                args=deploy_args,
                kwargs=deploy_kwargs,
            )
            contract_address = self.chain.wait.for_contract_address(deploy_transaction_hash)
            registrar = self.chain.registrar
            registrar.set_contract_address(contract_identifier, contract_address)
        else:
            deploy_transaction_hash = None

        return self.get_contract(contract_identifier), deploy_transaction_hash

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

    #
    # Utility
    #
    def link_bytecode(self, bytecode):
        """
        Return the fully linked contract bytecode.

        Note: This *must* use `get_contract` and **not** `get_contract_address`
        for resolution of link dependencies.  If it merely uses
        `get_contract_address` then the bytecode of sub-dependencies is not
        verified.
        """
        resolved_link_references = tuple((
            (link_reference, self.get_contract(link_reference.full_name).address)
            for link_reference
            in find_link_references(
                bytecode,
                self.chain.store.get_all_contract_names(),
            )
        ))

        linked_bytecode = link_bytecode(bytecode, resolved_link_references)
        return linked_bytecode

    @property
    def deployed_contracts(self):
        contract_classes = {
            contract_identifier: self.get_contract(contract_identifier)
            for contract_identifier
            in self.chain.store.get_all_contract_names()
            if self.is_contract_available(contract_identifier)
        }
        return package_contracts(contract_classes)
