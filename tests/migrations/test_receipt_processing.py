from eth_utils import (
    encode_hex,
)
from populus.migrations.deferred import (
    RegistrarValue,
    Address,
    UInt,
    generate_registrar_value_setters,
)


def test_special_case_for_address():
    address = '0xd3cda913deb6f67967b99d67acdfa1712c293601'
    value_setters = generate_registrar_value_setters(address)

    assert len(value_setters) == 1

    setter = value_setters[0]
    assert issubclass(setter, RegistrarValue)
    assert setter.value == address
    assert setter.value_type == 'address'


def test_special_case_for_txn_hash():
    txn_hash = '0xebb0f76aa6a6bb8d178ac2b54de2fd7ca738d704bf47d135c188ca7b6d35f2e4'
    value_setters = generate_registrar_value_setters(txn_hash)

    assert len(value_setters) == 1

    setter = value_setters[0]
    assert issubclass(setter, RegistrarValue)
    assert encode_hex(setter.value) == txn_hash
    assert setter.value_type == 'bytes32'


def test_single_value():
    v = UInt.defer(value=1)

    value_setters = generate_registrar_value_setters(v)

    assert len(value_setters) == 1

    setter = value_setters[0]
    assert issubclass(setter, RegistrarValue)
    assert setter.key == ''
    assert setter.value == 1
    assert setter.value_type == 'uint256'


def test_flat_array_of_receipts():
    v = [
        UInt.defer(value=1),
        UInt.defer(value=2),
    ]

    value_setters = generate_registrar_value_setters(v)

    assert len(value_setters) == 2

    setter_a, setter_b = value_setters
    assert issubclass(setter_a, RegistrarValue)
    assert setter_a.key == '0'
    assert setter_a.value == 1
    assert setter_a.value_type == 'uint256'

    assert setter_b.key == '1'
    assert setter_b.value == 2
    assert setter_b.value_type == 'uint256'


def test_flat_dict_of_receipts():
    v = {
        'key_a': UInt.defer(value=1),
        'key_b': UInt.defer(value=2),
    }

    value_setters = generate_registrar_value_setters(v)

    assert len(value_setters) == 2

    setter_a, setter_b = value_setters
    assert issubclass(setter_a, RegistrarValue)
    assert issubclass(setter_b, RegistrarValue)

    assert setter_a.value_type == 'uint256'
    assert setter_b.value_type == 'uint256'

    assert {setter_a.key, setter_b.key} == {'key_a', 'key_b'}
    assert {setter_a.value, setter_b.value} == {1, 2}


def test_nested_receipts():
    v = [
        UInt.defer(value=1),
        [
            UInt.defer(value=2),
            UInt.defer(value=3),
        ],
        {
            'key_a': UInt.defer(value=4),
            'key_b': [
                UInt.defer(value=5),
                UInt.defer(value=6),
            ],
            'key_c': {
                'key_d': UInt.defer(value=7),
                'key_e': UInt.defer(value=8),
                'key_f': Address.defer(
                    key='SomeContract',
                    value='0xd3cda913deb6f67967b99d67acdfa1712c293601',
                ),
            },
        },
    ]

    value_setters = generate_registrar_value_setters(v)

    assert len(value_setters) == 9

    expected_keys = {
        '0',
        '1/0',
        '1/1',
        '2/key_a',
        '2/key_b/0',
        '2/key_b/1',
        '2/key_c/key_d',
        '2/key_c/key_e',
        'SomeContract',
    }

    actual_keys = {s.key for s in value_setters}
    assert actual_keys == expected_keys


def test_key_prefixing():
    v = [
        UInt.defer(value=1),
        UInt.defer(key="some-global-value", value=2),
    ]

    value_setters = generate_registrar_value_setters(v, prefix=['a-prefix'])

    assert len(value_setters) == 2

    setter_a, setter_b = value_setters
    assert setter_a.key == 'a-prefix/0'
    assert setter_b.key == 'some-global-value'
