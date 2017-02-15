import pytest

from ethereum.tester import TransactionFailed

from populus.utils.testing import (
    load_contract_fixture,
)

from populus.migrations import (
    DeployContract,
    Address,
)


@load_contract_fixture('Math.sol')
def test_deploy_contract_operation_on_math_contract(web3, chain):
    MATH = chain.project.compiled_contracts['Math']

    deploy_contract_operation = DeployContract('Math', timeout=30)

    operation_receipt = deploy_contract_operation.execute(
        chain=chain,
        compiled_contracts={'Math': MATH},
    )
    deploy_txn_hash = operation_receipt['deploy-transaction-hash']
    contract_address = chain.wait.for_contract_address(deploy_txn_hash, timeout=30)

    code = web3.eth.getCode(contract_address)

    assert code == MATH['bytecode_runtime']


@load_contract_fixture('WithConstructorArguments.sol')
def test_deploy_contract_operation_with_arguments(web3, chain):
    WITH_CONSTRUCTOR_ARGUMENTS = chain.project.compiled_contracts['WithConstructorArguments']

    deploy_contract_operation = DeployContract(
        'WithConstructorArguments',
        timeout=30,
        arguments=[12345, 'a-string-argument-thats-32-bytes'],
    )

    operation_receipt = deploy_contract_operation.execute(
        chain=chain,
        compiled_contracts={'WithConstructorArguments': WITH_CONSTRUCTOR_ARGUMENTS},
    )
    deploy_txn_hash = operation_receipt['deploy-transaction-hash']
    contract_address = chain.wait.for_contract_address(deploy_txn_hash, timeout=30)

    code = web3.eth.getCode(contract_address)

    assert code == WITH_CONSTRUCTOR_ARGUMENTS['bytecode_runtime']

    ContractFactory = web3.eth.contract(**WITH_CONSTRUCTOR_ARGUMENTS)
    contract = ContractFactory(address=contract_address)

    assert contract.call().data_a() == 12345
    assert contract.call().data_b() == 'a-string-argument-thats-32-bytes'


@load_contract_fixture('ThrowsInConstructor.sol')
def test_deploy_contract_failure_during_deployment(web3, chain):
    THROWS_IN_CONSTRUCTOR = chain.project.compiled_contracts['ThrowsInConstructor']

    deploy_contract_operation = DeployContract(
        'ThrowsInConstructor',
        timeout=30,
        arguments=[True],
    )

    with pytest.raises(TransactionFailed):
        deploy_contract_operation.execute(
            chain=chain,
            compiled_contracts={'ThrowsInConstructor': THROWS_IN_CONSTRUCTOR},
        )
