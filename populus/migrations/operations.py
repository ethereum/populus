import types

from web3.utils.string import (
    force_text,
)

from populus.utils.contracts import (
    get_contract_library_dependencies,
)
from populus.utils.deploy import (
    deploy_contract,
)

from .registrar import (
    get_compiled_registrar_contract,
)
from .deferred import (
    Address,
    Resolver,
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
    timeout = 180

    def __init__(self, transaction, timeout=180):
        self.transaction = transaction
        self.timeout = timeout

    def execute(self, chain, **kwargs):
        resolver = Resolver(chain)

        transaction = {
            resolver(key): resolver(value)
            for key, value in resolver(self.transaction).items()
        }
        timeout = resolver(self.timeout)

        transaction_hash = chain.web3.eth.sendTransaction(transaction)
        if timeout is not None:
            chain.wait.for_receipt(transaction_hash, timeout=timeout)
        return {
            'transaction-hash': transaction_hash,
        }


class DeployContract(Operation):
    contract_name = None
    contract_registrar_name = None
    transaction = None
    timeout = 180
    libraries = None
    verify = True

    def __init__(self,
                 contract_name,
                 transaction=None,
                 arguments=None,
                 verify=True,
                 libraries=None,
                 timeout=180,
                 contract_registrar_name=None):
        if libraries is None:
            libraries = {}

        self.contract_name = contract_name
        self.contract_registrar_name = contract_registrar_name
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
        resolver = Resolver(chain)

        contract_name = resolver(self.contract_name)
        contract_registrar_name = resolver(self.contract_registrar_name)
        libraries = {
            resolver(key): resolver(value)
            for key, value in resolver(self.libraries).items()
        }
        transaction = {
            resolver(key): resolver(value)
            for key, value in resolver(self.transaction).items()
        }
        arguments = [
            resolver(arg) for arg in self.arguments
        ]
        timeout = resolver(self.timeout)
        verify = resolver(self.verify)

        contract_data = compiled_contracts[contract_name]
        BaseContractFactory = chain.web3.eth.contract(
            abi=contract_data['abi'],
            code=contract_data['code'],
            code_runtime=contract_data['code_runtime'],
            source=contract_data.get('source'),
        )

        all_known_contract_names = set(libraries.keys()).union(
            set(compiled_contracts.keys())
        )
        library_dependencies = get_contract_library_dependencies(
            BaseContractFactory.code,
            all_known_contract_names,
        )

        registrar = chain.registrar

        def resolve_library_link(library_name):
            registrar_key = "contract/{0}".format(library_name)

            if library_name in libraries:
                return libraries[library_name]
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
            contract_name=contract_name,
            contract_factory=BaseContractFactory,
            deploy_transaction=transaction,
            deploy_arguments=arguments,
            link_dependencies=link_dependencies,
        )

        if timeout is not None:
            contract_address = chain.wait.for_contract_address(
                deploy_transaction_hash,
                timeout=timeout,
            )
            if verify:
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
                'deploy-transaction-hash': deploy_transaction_hash,
                'canonical-contract-address': Address.defer(
                    key='contract/{name}'.format(
                        name=contract_registrar_name or contract_name,
                    ),
                    value=contract_address,
                ),
            }

        return {
            'deploy-transaction-hash': deploy_transaction_hash,
        }


class TransactContract(Operation):
    contract_address = None
    contract_name = None
    method_name = None
    arguments = None
    transaction = None

    timeout = 180

    def __init__(self,
                 contract_address,
                 contract_name,
                 method_name,
                 arguments=None,
                 transaction=None,
                 timeout=180):
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
        resolver = Resolver(chain)

        contract_address = resolver(self.contract_address)
        contract_name = resolver(self.contract_name)
        transaction = {
            resolver(key): resolver(value)
            for key, value in resolver(self.transaction).items()
        }
        arguments = [
            resolver(arg) for arg in self.arguments
        ]
        method_name = resolver(self.method_name)
        timeout = resolver(self.timeout)

        if not contract_address:
            raise ValueError("cannot transact without an address")

        contract_data = compiled_contracts[contract_name]
        contract = chain.web3.eth.contract(
            address=contract_address,
            abi=contract_data['abi'],
            code=contract_data['code'],
            code_runtime=contract_data['code_runtime'],
            source=contract_data.get('source'),
        )

        transactor = contract.transact(transaction)
        method = getattr(transactor, method_name)
        transaction_hash = method(*arguments)

        if timeout is not None:
            chain.wait.for_receipt(transaction_hash, timeout=timeout)

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
        compiled_contracts = {
            'Registrar': get_compiled_registrar_contract(),
        }
        return super(DeployRegistrar, self).execute(
            chain=chain,
            compiled_contracts=compiled_contracts,
            **kwargs
        )
