from populus.migrations import (
    TransactContract,
)


def test_transact_contract_operation(web3, chain, math, MATH):
    transact_contract_operation = TransactContract(
        contract_name='Math',
        method_name='increment',
        arguments=[3],
        contract_address=math.address,
        timeout=30,
    )

    before_value = math.call().counter()

    transact_txn_hash = transact_contract_operation.execute(
        chain=chain,
        compiled_contracts={'Math': MATH},
        transaction={'gas': 200000},
    )['transaction-hash']
    chain.wait.for_receipt(transact_txn_hash, timeout=30)

    after_value = math.call().counter()

    assert after_value - before_value == 3
