import pytest

from populus.utils.transactions import (
    wait_for_transaction_receipt,
    get_contract_address_from_txn,
)
from populus.migrations.registrar import (
    get_compiled_registrar_contract,
    DeployRegistrar,
)


def test_deploy_registrar_operation(web3):
    registrar_deploy_txn = DeployRegistrar().execute(web3=web3)
    registrar_address = get_contract_address_from_txn(web3, registrar_deploy_txn, timeout=30)

    assert registrar_address

    registrar = get_compiled_registrar_contract(web3, registrar_address)

    assert registrar


def test_setting_bytes32(web3, registrar):
    set_txn = registrar.transact().set('this-is-a-key', 'this-is-a-value')
    wait_for_transaction_receipt(web3, set_txn, timeout=30)

    value = registrar.call().get('this-is-a-key')

    assert len(value) == 32
    assert 'this-is-a-value' in value


def test_setting_address(web3, registrar):
    set_txn = registrar.transact().setAddress('this-is-a-key', '0xd3cda913deb6f67967b99d67acdfa1712c293601')
    wait_for_transaction_receipt(web3, set_txn, timeout=30)

    value = registrar.call().getAddress('this-is-a-key')
    assert value == '0xd3cda913deb6f67967b99d67acdfa1712c293601'


@pytest.mark.parametrize(
    'value',
    (0, 1, 1234567890, 2**256 - 1),
)
def test_setting_uint(web3, registrar, value):
    set_txn = registrar.transact().setUInt('this-is-a-key', value)
    wait_for_transaction_receipt(web3, set_txn, timeout=30)

    chain_value = registrar.call().getUInt('this-is-a-key')

    assert chain_value == value


@pytest.mark.parametrize(
    'value',
    (0, 1, -1, 1234567890, 2**255 - 1),
)
def test_setting_int(web3, registrar, value):
    set_txn = registrar.transact().setInt('this-is-a-key', value)
    wait_for_transaction_receipt(web3, set_txn, timeout=30)

    chain_value = registrar.call().getInt('this-is-a-key')

    assert chain_value == value


@pytest.mark.parametrize(
    'value',
    ('', 'a', 'some-short-string', 'some-string-that-is-longer-than-32-bytes'),
)
def test_setting_string(web3, registrar, value):
    set_txn = registrar.transact().setString('this-is-a-key', value)
    wait_for_transaction_receipt(web3, set_txn, timeout=30)

    chain_value = registrar.call().getString('this-is-a-key')

    assert chain_value == value


def test_exists_query(web3, registrar):
    assert registrar.call().exists('this-is-a-key') is False

    set_txn = registrar.transact().set('this-is-a-key', 'a-value')
    wait_for_transaction_receipt(web3, set_txn, timeout=30)

    assert registrar.call().exists('this-is-a-key') is True
