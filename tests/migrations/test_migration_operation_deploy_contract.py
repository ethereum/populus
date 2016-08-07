import pytest

from populus.migrations import (
    DeployContract,
    Address,
)
from populus.utils.transactions import (
    wait_for_transaction_receipt,
    get_contract_address_from_txn,
)
from populus.utils.contracts import (
    link_contract,
)


def test_deploy_contract_operation_on_math_contract(web3, MATH):
    deploy_contract_operation = DeployContract('Math', timeout=30)

    operation_receipt = deploy_contract_operation.execute(
        web3=web3,
        compiled_contracts={'Math': MATH},
    )
    deploy_txn_hash = operation_receipt['deploy-transaction-hash']
    contract_address = get_contract_address_from_txn(web3, deploy_txn_hash, timeout=30)

    code = web3.eth.getCode(contract_address)

    assert code == MATH['code_runtime']


def test_deploy_contract_operation_with_arguments(web3, WITH_CONSTRUCTOR_ARGUMENTS):
    deploy_contract_operation = DeployContract(
        'WithConstructorArguments',
        timeout=30,
        arguments=[12345, 'a-string-argument-thats-32-bytes'],
    )

    operation_receipt = deploy_contract_operation.execute(
        web3=web3,
        compiled_contracts={'WithConstructorArguments': WITH_CONSTRUCTOR_ARGUMENTS},
    )
    deploy_txn_hash = operation_receipt['deploy-transaction-hash']
    contract_address = get_contract_address_from_txn(web3, deploy_txn_hash, timeout=30)

    code = web3.eth.getCode(contract_address)

    assert code == WITH_CONSTRUCTOR_ARGUMENTS['code_runtime']

    ContractFactory = web3.eth.contract(**WITH_CONSTRUCTOR_ARGUMENTS)
    contract = ContractFactory(address=contract_address)

    assert contract.call().data_a() == 12345
    assert contract.call().data_b() == b'a-string-argument-thats-32-bytes'


def test_deploy_contract_failure_during_deployment(web3, THROWER):
    deploy_contract_operation = DeployContract(
        'Thrower',
        timeout=30,
        arguments=[True],
    )

    with pytest.raises(ValueError):
        deploy_contract_operation.execute(
            web3=web3,
            compiled_contracts={'Thrower': THROWER},
        )


def test_deployment_with_library_linking(web3, LIBRARY_13, MULTIPLY_13, registrar):
    Library13 = web3.eth.contract(**LIBRARY_13)
    Multiply13 = web3.eth.contract(**MULTIPLY_13)

    library_deploy_txn_hash = Library13.deploy()
    library_13_address = get_contract_address_from_txn(web3, library_deploy_txn_hash, 30)

    assert web3.eth.getCode(library_13_address) == LIBRARY_13['code_runtime']

    set_library_addr_txn_hash = registrar.transact().setAddress(
        'contract/Library13',
        library_13_address,
    )
    wait_for_transaction_receipt(web3, set_library_addr_txn_hash, 30)

    deploy_operation = DeployContract(
        'Multiply13',
        timeout=30,
        libraries={
            'Library13': Address.defer(key='contract/Library13'),
        },
    )

    assert '__Library13__' in Multiply13.code
    assert '__Library13__' in Multiply13.code_runtime

    operation_receipt = deploy_operation.execute(
        web3=web3,
        compiled_contracts={'Multiply13': MULTIPLY_13},
        registrar=registrar,
    )
    deploy_txn_hash = operation_receipt['deploy-transaction-hash']
    contract_address = get_contract_address_from_txn(web3, deploy_txn_hash, timeout=30)

    lib_contract = web3.eth.contract(address=library_13_address, **LIBRARY_13)
    _should_be_39 = lib_contract.call().multiply13(3)
    contract = web3.eth.contract(address=contract_address, **MULTIPLY_13)
    code = web3.eth.getCode(contract_address)
    should_be_39 = contract.call().multiply13(3)
    assert should_be_39 == 39
