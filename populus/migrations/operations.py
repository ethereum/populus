import types

from solc import compile_source

from web3.utils.string import (
    force_text,
)

from populus.utils.transactions import (
    wait_for_transaction_receipt,
    get_contract_address_from_txn,
)
from populus.utils.contracts import (
    get_contract_library_dependencies,
)
from populus.utils.deploy import (
    deploy_contract,
)

from .registrar import (
    REGISTRAR_SOURCE,
)
from .deferred import (
    Address,
    resolve_if_deferred_value,
)


class Operation(object):
    """
    Base class that all migration operations inherit from.
    """
    def execute(self, **kwargs):
        raise NotImplementedError(
            "The `execute` method must be implemented by each Operation subclass"
        )

    def deconstruct(self):
        deferred_kwargs = {
            key: getattr(self, key)
            for key in dir(self)
            if all((
                # magic methods
                not key.startswith('__'),
                # functions
                not isinstance(getattr(self, key), types.FunctionType),
                # methods
                not isinstance(getattr(self, key), types.MethodType),
                # attributes that are either not present on the parent class or
                # don't match the version found on the parent class.
                (
                    not hasattr(type(self), key) or
                    getattr(self, key) != getattr(type(self), key)
                ),
            ))
        }
        return (
            '.'.join((self.__class__.__module__, self.__class__.__name__)),
            tuple(),
            deferred_kwargs,
        )


class RunPython(Operation):
    """
    A migration operation that runs custom python code for executing operations
    that don't fit within the provided operation canvas.
    """
    def __init__(self, callback):
        self.callback = callback

    def execute(self, **kwargs):
        return self.callback(**kwargs)


class SendTransaction(Operation):
    """
    A migration operation that sends a transaction.
    """
    transaction = None
    timeout = 120

    def __init__(self, transaction, timeout=120):
        self.transaction = transaction
        if timeout is not None:
            self.timeout = timeout

    def execute(self, chain, **kwargs):
        transaction = {
            key: resolve_if_deferred_value(value, chain)
            for key, value in self.transaction.items()
        }
        transaction_hash = chain.web3.eth.sendTransaction(transaction)
        if self.timeout is not None:
            wait_for_transaction_receipt(
                chain.web3, transaction_hash, timeout=self.timeout,
            )
        return {
            'transaction-hash': transaction_hash,
        }


class DeployContract(Operation):
    contract = None
    transaction = None
    timeout = None
    libraries = None
    verify = None

    def __init__(self,
                 contract_name,
                 transaction=None,
                 arguments=None,
                 verify=True,
                 libraries=None,
                 timeout=120):
        if libraries is None:
            libraries = {}

        self.contract_name = contract_name
        self.libraries = libraries

        if timeout is None and verify:
            raise ValueError(
                "Invalid configuration.  When verifying a contracts deployment, "
                "the timeout value must be set."
            )

        if transaction is None:
            transaction = {}

        if 'data' in transaction or 'to' in transaction:
            raise ValueError(
                "Invalid configuration.  You cannot specify `data` or `to` "
                "values in `DeployContract` transactions."
            )

        if arguments is None:
            arguments = []

        self.transaction = transaction
        self.arguments = arguments
        self.verify = verify

        if timeout is not None:
            self.timeout = timeout

    def execute(self, chain, compiled_contracts, **kwargs):
        contract_data = compiled_contracts[self.contract_name]
        BaseContractFactory = chain.web3.eth.contract(
            abi=contract_data['abi'],
            code=contract_data['code'],
            code_runtime=contract_data['code_runtime'],
            source=contract_data['source'],
        )

        all_known_contract_names = set(self.libraries.keys()).union(
            set(compiled_contracts.keys())
        )
        library_dependencies = get_contract_library_dependencies(
            BaseContractFactory.code,
            all_known_contract_names,
        )

        registrar = chain.registrar

        def resolve_library_link(library_name):
            registrar_key = "contract/{0}".format(library_name)

            if library_name in self.libraries:
                return resolve_if_deferred_value(self.libraries[library_name], chain)
            elif registrar.call().exists(registrar_key):
                library_address = registrar.call().getAddress(registrar_key)
                # TODO: implement validation that this contract address is
                # in fact the library we want to link against.
                return library_address
            else:
                raise ValueError(
                    "Unable to find address for library '{0}'".format(library_name)
                )

        link_dependencies = {
            dependency_name: resolve_library_link(dependency_name)
            for dependency_name
            in library_dependencies
        }

        deploy_transaction_hash, contract_factory = deploy_contract(
            chain=chain,
            contract_name=self.contract_name,
            contract_factory=BaseContractFactory,
            deploy_transaction=self.transaction,
            deploy_arguments=self.arguments,
            link_dependencies=link_dependencies,
        )

        if self.timeout is not None:
            contract_address = get_contract_address_from_txn(
                chain.web3, deploy_transaction_hash, timeout=self.timeout,
            )
            if self.verify:
                code = force_text(chain.web3.eth.getCode(contract_address))
                expected_code = force_text(contract_factory.code_runtime)
                if code != expected_code:
                    raise ValueError(
                        "Bytecode @ {0} does not match expected contract "
                        "bytecode.\n\n"
                        "expected : '{1}'\n"
                        "actual   : '{2}'\n".format(
                            contract_address,
                            expected_code,
                            code,
                        ),
                    )
            return {
                'contract-address': contract_address,
                'deploy-transaction-hash': deploy_transaction_hash,
                'canonical-contract-address': Address.defer(
                    key='/'.join(('contract', self.contract_name)),
                    value=contract_address,
                ),
            }

        return {
            'deploy-transaction-hash': deploy_transaction_hash,
        }


class TransactContract(Operation):
    contract_name = None
    method_name = None
    arguments = None
    transaction = None

    timeout = None

    def __init__(self,
                 contract_name,
                 method_name,
                 arguments=None,
                 transaction=None,
                 contract_address=None,
                 timeout=120):
        self.contract_address = contract_address
        self.contract_name = contract_name
        self.method_name = method_name

        if arguments is None:
            arguments = []
        self.arguments = arguments

        if transaction is None:
            transaction = {}

        self.transaction = transaction

        if timeout is not None:
            self.timeout = timeout

    def execute(self, chain, compiled_contracts, **kwargs):
        contract_name = resolve_if_deferred_value(self.contract_name, chain=chain)
        contract_address = resolve_if_deferred_value(
            self.contract_address,
            chain=chain,
        )

        if not contract_address:
            raise ValueError("cannot transact without an address")

        contract_data = compiled_contracts[contract_name]
        contract = chain.web3.eth.contract(
            address=contract_address,
            abi=contract_data['abi'],
            code=contract_data['code'],
            code_runtime=contract_data['code_runtime'],
            source=contract_data['source'],
        )

        arguments = [resolve_if_deferred_value(arg, chain=chain) for arg in self.arguments]
        method_name = resolve_if_deferred_value(self.method_name, chain=chain)

        transactor = contract.transact(self.transaction)
        method = getattr(transactor, method_name)
        transaction_hash = method(*arguments)

        if self.timeout is not None:
            wait_for_transaction_receipt(
                chain.web3, transaction_hash, timeout=self.timeout,
            )

        return {
            'transaction-hash': transaction_hash,
        }


class DeployRegistrar(DeployContract):
    def __init__(self, **kwargs):
        super(DeployRegistrar, self).__init__(
            contract_name="Registrar",
            **kwargs
        )

    def execute(self, chain, **kwargs):
        kwargs.pop('compiled_contracts', None)
        compiled_contracts = compile_source(REGISTRAR_SOURCE)
        return super(DeployRegistrar, self).execute(
            chain=chain,
            compiled_contracts=compiled_contracts,
            **kwargs
        )
