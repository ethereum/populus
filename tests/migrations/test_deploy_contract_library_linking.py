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


def test_deployment_with_library_linking(project_dir, web3, LIBRARY_13, MULTIPLY_13, chain):
    registrar = chain.registrar

    Library13 = web3.eth.contract(**LIBRARY_13)
    Multiply13 = web3.eth.contract(**MULTIPLY_13)

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = get_contract_address_from_txn(web3, library_deploy_txn_hash, 30)

    assert library_deploy_txn['input'] == LIBRARY_13['code']
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
        chain,
        compiled_contracts={'Multiply13': MULTIPLY_13},
    )
    deploy_txn_hash = operation_receipt['deploy-transaction-hash']
    deploy_txn = web3.eth.getTransaction(deploy_txn_hash)
    contract_address = get_contract_address_from_txn(web3, deploy_txn_hash, timeout=30)

    print('Contract:', contract_address)

    # verify on chain code is the correctly linked code.
    from populus.utils.contracts import link_contract
    expected_code = link_contract(MULTIPLY_13['code'], **{'Library13': library_13_address})
    expected_runtime = link_contract(MULTIPLY_13['code_runtime'], **{'Library13': library_13_address})

    assert deploy_txn['input'] == expected_code
    assert web3.eth.getCode(contract_address) == expected_runtime

    lib_contract = web3.eth.contract(address=library_13_address, **LIBRARY_13)
    _should_be_39 = lib_contract.call().multiply13(3)
    assert _should_be_39 == 39
    contract = web3.eth.contract(address=contract_address, **MULTIPLY_13)

    should_be_39 = contract.call().multiply13(3)
    assert should_be_39 == 39
