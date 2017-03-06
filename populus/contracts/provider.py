import itertools

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
    link_bytecode,
    find_link_references,
)

from .exceptions import (
    UnknownContract,
    NoKnownAddress,
    BytecodeMismatch,
)


def get_base_contract_factory(contract_identifier, store_backends):
    for _, backend in store_backends.items():
        try:
            return backend.get_base_contract_factory(contract_identifier)
        except UnknownContract:
            pass
    else:
        raise UnknownContract(
            "No contract data was available for the contract identifier '{0}' "
            "from any of the configured backends".format(contract_identifier)
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
            contract_addresses = self.chain.registrar.get_contract_addresses(contract_identifier)
        except NoKnownAddress:
            return False

        if len(contract_addresses) == 1:
            contract_address = contract_addresses[0]
        else:
            raise NotImplementedError(
                "Handling of multiple contract addresses has not been implemented"
            )

        if not self.are_contract_dependencies_available(contract_identifier):
            return False

        ContractFactory = self.get_contract_factory(contract_identifier)
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
        ContractFactory = self.get_contract_factory(contract_identifier)
        contract_addresses = self.chain.registrar.get_contract_addresses(contract_identifier)

        if len(contract_addresses) == 1:
            contract_address = contract_addresses[0]
        else:
            raise NotImplementedError(
                "Handling of multiple contract addresses has not been implemented"
            )

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

        ContractFactory = self.get_contract_factory(contract_identifier)
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

    #
    # Store API
    #
    def get_base_contract_factory(self, contract_identifier):
        """
        Returns the base contract factory for the given `contract_identifier`.
        The `bytecode` and `bytecode_runtime` will be unlinked in this class.
        """
        return get_base_contract_factory(contract_identifier, self.provider_backends)

    def get_contract_data(self, contract_identifier):
        """
        Returns a dictionary containing the compiler output for the given
        contract identifier.
        """
        for backend in self.provider_backends.value():
            try:
                return backend.get_contract_data(contract_identifier)
            except UnknownContract:
                continue
        else:
            raise UnknownContract(
                "No contracts found for the contract identifier '{0}'".format(
                    contract_identifier,
                )
            )

    def get_all_contract_data(self):
        """
        Returns a dictionary mapping all contract identifiers to their contract data.
        """
        return dict(itertools.chain.from_iterable(
            backend.get_all_contract_data().items()
            for backend
            in self.provider_backends.values()
        ))

    def get_all_contract_names(self):
        """
        Returns a set of all of the known contract identifiers.
        """
        return set(itertools.chain.from_iterable(
            backend.get_all_contract_names()
            for backend
            in self.provider_backends.values()
        ))

    def get_contract_factory(self, contract_identifier):
        """
        Returns the contract factory for the given `contract_identifier`.  The
        `bytecode` and `bytecode_runtime` values for this factory will be fully
        linked.
        """
        if contract_identifier in self._factory_cache:
            return self._factory_cache[contract_identifier]

        BaseContractFactory = self.get_base_contract_factory(contract_identifier)

        bytecode = self.link_bytecode(BaseContractFactory.bytecode)
        bytecode_runtime = self.link_bytecode(BaseContractFactory.bytecode_runtime)

        ContractFactory = BaseContractFactory.factory(
            web3=BaseContractFactory.web3,
            bytecode=bytecode,
            bytecode_runtime=bytecode_runtime,
        )

        self._factory_cache[contract_identifier] = ContractFactory
        return ContractFactory

    #
    # Private API
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
            (link_reference, self.chain.provider.get_contract(link_reference.full_name).address)
            for link_reference
            in find_link_references(
                bytecode,
                self.get_all_contract_names(),
            )
        ))

        linked_bytecode = link_bytecode(bytecode, resolved_link_references)
        return linked_bytecode
