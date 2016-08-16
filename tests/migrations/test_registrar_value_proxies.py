import pytest

from populus.utils.transactions import (
    wait_for_transaction_receipt,
)

from populus.migrations import (
    Address,
    Bytes32,
    String,
    UInt,
    Int,
    Bool,
)


@pytest.mark.parametrize(
    'RegistrarValueClass,value,setter',
    (
        (Address, '0xd3cda913deb6f67967b99d67acdfa1712c293601', 'setAddress'),
        (Bytes32, 'abcdefghijklmnopqrstuvwxyz012345', 'set'),
        (UInt, 1234567890, 'setUInt'),
        (Int, 1234567890, 'setInt'),
        (Int, -1234567890, 'setInt'),
        (String, 'abcdefghijklmnopqrstuvwxyz012345', 'setString'),
        (String, 'abcdefghijklmnopqrstuvwxyz01234567890', 'setString'),
        (Bool, True, 'setBool'),
        (Bool, False, 'setBool'),
    )
)
def test_registrar_value_getting(web3, chain, RegistrarValueClass, value,
                                 setter):
    registrar = chain.registrar
    set_txn = getattr(registrar.transact(), setter)('k', value)
    wait_for_transaction_receipt(web3, set_txn, timeout=30)

    value_proxy = RegistrarValueClass(chain, key='k')
    assert value_proxy.get() == value



@pytest.mark.parametrize(
    'RegistrarValueClass,value,getter',
    (
        (Address, '0xd3cda913deb6f67967b99d67acdfa1712c293601', 'getAddress'),
        (Bytes32, 'abcdefghijklmnopqrstuvwxyz012345', 'get'),
        (UInt, 1234567890, 'getUInt'),
        (Int, 1234567890, 'getInt'),
        (Int, -1234567890, 'getInt'),
        (String, 'abcdefghijklmnopqrstuvwxyz012345', 'getString'),
        (String, 'abcdefghijklmnopqrstuvwxyz01234567890', 'getString'),
        (Bool, True, 'getBool'),
        (Bool, False, 'getBool'),
    )
)
def test_registrar_value_setting(web3, chain, RegistrarValueClass, value,
                                 getter):
    registrar = chain.registrar
    value_proxy = RegistrarValueClass(chain, key='k')
    value_proxy.set(value, timeout=30)

    chain_value = getattr(registrar.call(), getter)('k')

    assert chain_value == value
