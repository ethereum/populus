from populus.migrations.registrar import (
    ReceiptValue,
    RegistrarValue,
    generate_registrar_value_setters,
)


def test_special_case_for_address():
    address = '0xd3cda913deb6f67967b99d67acdfa1712c293601'
    value_setters = generate_registrar_value_setters(address)

    assert len(value_setters) == 1

    setter = value_setters[0]
    assert isinstance(setter, RegistrarValue)
    assert setter.value == address
    assert setter.value_type == 'address'


def test_special_case_for_txn_hash():
    txn_hash = '0xebb0f76aa6a6bb8d178ac2b54de2fd7ca738d704bf47d135c188ca7b6d35f2e4'
    value_setters = generate_registrar_value_setters(txn_hash)

    assert len(value_setters) == 1

    setter = value_setters[0]
    assert isinstance(setter, RegistrarValue)
    assert setter.value == txn_hash
    assert setter.value_type == 'bytes32'


def test_single_value():
    v = ReceiptValue(1, 'uint256')

    value_setters = generate_registrar_value_setters(v)

    assert len(value_setters) == 1

    setter = value_setters[0]
    assert isinstance(setter, RegistrarValue)
    assert setter.key == ''
    assert setter.value == 1
    assert setter.value_type == 'uint256'


def test_flat_array_of_receipts():
    v = [
        ReceiptValue(1, 'uint256'),
        ReceiptValue(2, 'uint256'),
    ]

    value_setters = generate_registrar_value_setters(v)

    assert len(value_setters) == 2

    setter_a, setter_b = value_setters
    assert isinstance(setter_a, RegistrarValue)
    assert setter_a.key == '0'
    assert setter_a.value == 1
    assert setter_a.value_type == 'uint256'

    assert setter_b.key == '1'
    assert setter_b.value == 2
    assert setter_b.value_type == 'uint256'


def test_flat_dict_of_receipts():
    v = {
        'key_a': ReceiptValue(1, 'uint256'),
        'key_b': ReceiptValue(2, 'uint256'),
    }

    value_setters = generate_registrar_value_setters(v)

    assert len(value_setters) == 2

    setter_a, setter_b = value_setters
    assert isinstance(setter_a, RegistrarValue)
    assert isinstance(setter_b, RegistrarValue)

    assert setter_a.value_type == 'uint256'
    assert setter_b.value_type == 'uint256'

    assert {setter_a.key, setter_b.key} == {'key_a', 'key_b'}
    assert {setter_a.value, setter_b.value} == {1, 2}


def test_nested_receipts():
    v = [
        ReceiptValue(1, 'uint256'),
        [
            ReceiptValue(2, 'uint256'),
            ReceiptValue(3, 'uint256'),
        ],
        {
            'key_a': ReceiptValue(4, 'uint256'),
            'key_b': [
                ReceiptValue(5, 'uint256'),
                ReceiptValue(6, 'uint256'),
            ],
            'key_c': {
                'key_d': ReceiptValue(7, 'uint256'),
                'key_e': ReceiptValue(8, 'uint256'),
            },
        },
    ]

    value_setters = generate_registrar_value_setters(v)

    assert len(value_setters) == 8

    expected_keys = {
        '0',
        '1/0',
        '1/1',
        '2/key_a',
        '2/key_b/0',
        '2/key_b/1',
        '2/key_c/key_d',
        '2/key_c/key_e',
    }

    actual_keys = {s.key for s in value_setters}
    assert actual_keys == expected_keys


def test_key_prefixing():
    v = [ReceiptValue(1, 'uint256')]

    value_setters = generate_registrar_value_setters(v, prefix=['a-prefix'])

    assert len(value_setters) == 1

    setter = value_setters[0]
    assert setter.key == 'a-prefix/0'
