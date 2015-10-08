import pytest


from populus.contracts import (
    deploy_contract,
)
from populus.utils import (
    get_contract_address_from_txn,
)


@pytest.fixture(autouse=True)
def _rpc_server(testrpc_server):
    return testrpc_server


def test_deployment_with_no_args(blockchain_client, Math):
    deploy_txn_hash = deploy_contract(
        blockchain_client,
        Math,
    )
    contract_addr = get_contract_address_from_txn(blockchain_client, deploy_txn_hash)
    assert contract_addr


def test_deployment_with_endowment(blockchain_client, Math):
    deploy_txn_hash = deploy_contract(
        blockchain_client,
        Math,
        value=1000,
    )
    contract_addr = get_contract_address_from_txn(blockchain_client, deploy_txn_hash)
    assert contract_addr
    math = Math(contract_addr, blockchain_client)
    assert math.get_balance() == 1000


def test_deployment_with_args(blockchain_client, Named):
    deploy_txn_hash = deploy_contract(
        blockchain_client,
        Named,
        constructor_args=("John",),
    )
    contract_addr = get_contract_address_from_txn(blockchain_client, deploy_txn_hash)

    named = Named(contract_addr, blockchain_client)
    name = named.name.call()
    assert name == "John"
