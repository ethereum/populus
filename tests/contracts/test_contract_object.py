import pytest

from eth_rpc_client import Client

from populus.contracts import Contract

from ethereum.abi import ContractTranslator
from ethereum import utils as ethereum_utils


def test_contract_deploy(math_contract_meta, rpc_server, rpc_client, eth_coinbase):
    Math = Contract(math_contract_meta, 'Math')
    deploy_txn_hash = Math.deploy(_from=eth_coinbase)
    receipt = rpc_client.get_transaction_receipt(deploy_txn_hash)
    assert receipt
    assert receipt['contractAddress']


@pytest.fixture
def math(rpc_server, rpc_client, eth_coinbase):
    Math = Contract(contract, 'Math')

    txn_hash = Math.deploy(_from=eth_coinbase)
    receipt = rpc_client.get_transaction_receipt(txn_hash)

    math = Math(receipt['contractAddress'])
    return math


def test_contract_return13_function_signature(math):
    assert math.return13.function.abi_function_signature == 371289913
    assert math.return13.function.encoded_abi_function_signature == '\x16!o9'
    assert math.return13.function.get_call_data([]) == '16216f39'


def test_contract_add_function_signature(math):
    assert math.add.function.abi_function_signature == 2784215611
    assert math.add.function.encoded_abi_function_signature == '\xa5\xf3\xc2;'
    assert math.add.function.get_call_data((3, 4)) == 'a5f3c23b00000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004'


def test_contract_multiply7_function_signature(math):
    assert math.multiply7.function.abi_function_signature == 3707058097
    assert math.multiply7.function.encoded_abi_function_signature == '\xdc\xf57\xb1'
    assert math.multiply7.function.get_call_data((3,)) == 'dcf537b10000000000000000000000000000000000000000000000000000000000000003'


def test_contract_function_call_return13(math, eth_coinbase):
    ret = math.return13.call(_from=eth_coinbase)
    assert ret == 13


def test_contract_function_call_multiply7(math, eth_coinbase):
    ret = math.multiply7.call(3, _from=eth_coinbase)
    assert ret == 21


def test_contract_function_call_add(math, eth_coinbase):
    ret = math.add.call(25, 35, _from=eth_coinbase)
    assert ret == 60


def test_sent_transaction_with_value(math, eth_coinbase, rpc_client):
    assert math.get_balance() == 0
    txn_hash = math.add.sendTransaction(35, 45, _from=eth_coinbase, value=1000)
    assert math.get_balance() == 1000
