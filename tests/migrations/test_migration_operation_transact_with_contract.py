from populus.migrations import (
    TransactContract,
)
from populus.utils.transactions import (
    wait_for_transaction_receipt,
)


def test_transact_contract_operation(web3, math, MATH):
    transact_contract_operation = TransactContract(
        contract_name='Math',
        method_name='increment',
        arguments=[3],
        contract_address=math.address,
        timeout=30,
    )

    before_value = math.call().counter()

    transact_txn_hash = transact_contract_operation.execute(
        web3=web3,
        compiled_contracts={'Math': MATH},
        transaction={'gas': 200000},
    )
    wait_for_transaction_receipt(web3, transact_txn_hash, timeout=30)

    after_value = math.call().counter()

    assert after_value - before_value == 3
