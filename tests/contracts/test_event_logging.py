import pytest

from populus.contracts import (
    deploy_contract,
)
from populus.utils import (
    get_contract_address_from_txn,
    wait_for_transaction,
)


@pytest.fixture(autouse=True)
def _rpc_server(rpc_server):
    return rpc_server


@pytest.fixture()
def deployed_logs_events(LogsEvents, rpc_server, blockchain_client):
    deploy_txn_hash = deploy_contract(
        blockchain_client,
        LogsEvents,
    )
    contract_addr = get_contract_address_from_txn(
        blockchain_client,
        deploy_txn_hash,
    )
    assert contract_addr
    logs_events = LogsEvents(contract_addr, blockchain_client)
    return logs_events


def test_it(deployed_logs_events, blockchain_client):
    txn_hash = deployed_logs_events.logDoubleIndex('test-key-a', 'test-key-b', 'test-val_a', 12345)
    txn_receipt = wait_for_transaction(blockchain_client, txn_hash)
    txn = blockchain_client.get_transaction_by_hash(txn_hash)
    block = blockchain_client.get_block_by_number(int(txn_receipt['blockNumber'], 16))
    assert False
    x = 3
