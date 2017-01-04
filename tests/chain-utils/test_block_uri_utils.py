import pytest

from populus.utils.chains import (
    is_block_or_transaction_hash,
    create_block_uri,
    create_transaction_uri,
    is_BIP122_block_uri,
    is_BIP122_transaction_uri,
    parse_BIP122_uri,
)


HASH_A = '0x1234567890123456789012345678901234567890123456789012345678901234'
HASH_A_NO_PREFIX = '1234567890123456789012345678901234567890123456789012345678901234'
HASH_B = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
HASH_B_NO_PREFIX = '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
BLOCK_URI = 'blockchain://{0}/block/{1}'.format(HASH_A_NO_PREFIX, HASH_B_NO_PREFIX)
TRANSACTION_URI = 'blockchain://{0}/transaction/{1}'.format(HASH_A_NO_PREFIX, HASH_B_NO_PREFIX)


@pytest.mark.parametrize(
    'value,expected',
    (
        (HASH_A, True),
        (HASH_A_NO_PREFIX, True),
        ('', False),
        ('0x', False),
        (HASH_A[:-1], False),
        (HASH_A_NO_PREFIX[:-1], False),
    )
)
def test_is_block_or_transaction_hash(value, expected):
    actual = is_block_or_transaction_hash(value)
    assert actual is expected


@pytest.mark.parametrize(
    'chain_id,block_hash,expected',
    (
        (
            HASH_A,
            HASH_B,
            BLOCK_URI,
        ),
        (
            HASH_A_NO_PREFIX,
            HASH_B_NO_PREFIX,
            BLOCK_URI,
        ),
    ),
)
def test_create_block_uri(chain_id, block_hash, expected):
    actual = create_block_uri(chain_id, block_hash)
    assert actual == expected


@pytest.mark.parametrize(
    'chain_id,transaction_hash,expected',
    (
        (
            HASH_A,
            HASH_B,
            TRANSACTION_URI,
        ),
        (
            HASH_A_NO_PREFIX,
            HASH_B_NO_PREFIX,
            TRANSACTION_URI,
        ),
    ),
)
def test_create_transaction_uri(chain_id, transaction_hash, expected):
    actual = create_transaction_uri(chain_id, transaction_hash)
    assert actual == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        (BLOCK_URI, True),
        (TRANSACTION_URI, False),
        ('blockchain://{0}/block/{1}'.format(HASH_A, HASH_B_NO_PREFIX), False),
        ('blockchain://{0}/block/{1}'.format(HASH_A_NO_PREFIX, HASH_B), False),
        ('blockchain://{0}/block/{1}'.format(HASH_A, HASH_B_NO_PREFIX), False),
        ('blockchain://{0}/block/{1}'.format(HASH_A_NO_PREFIX[:-1], HASH_B_NO_PREFIX), False),
        ('blockchain://{0}/block/{1}'.format(HASH_A_NO_PREFIX, HASH_B_NO_PREFIX[:-1]), False),
    ),
)
def test_is_BIP122_block_uri(value, expected):
    actual = is_BIP122_block_uri(value)
    assert actual is expected


@pytest.mark.parametrize(
    'value,expected',
    (
        (TRANSACTION_URI, True),
        (BLOCK_URI, False),
        ('blockchain://{0}/transaction/{1}'.format(HASH_A, HASH_B_NO_PREFIX), False),
        ('blockchain://{0}/transaction/{1}'.format(HASH_A_NO_PREFIX, HASH_B), False),
        ('blockchain://{0}/transaction/{1}'.format(HASH_A, HASH_B_NO_PREFIX), False),
        ('blockchain://{0}/transaction/{1}'.format(HASH_A_NO_PREFIX[:-1], HASH_B_NO_PREFIX), False),
        ('blockchain://{0}/transaction/{1}'.format(HASH_A_NO_PREFIX, HASH_B_NO_PREFIX[:-1]), False),
    ),
)
def test_is_BIP122_transaction_uri(value, expected):
    actual = is_BIP122_transaction_uri(value)
    assert actual is expected


@pytest.mark.parametrize(
    'value, expected_resource_type',
    (
        (TRANSACTION_URI, 'transaction'),
        (BLOCK_URI, 'block'),
    ),
)
def test_pars_BIP122_uri(value, expected_resource_type):
    chain_id, resource_type, resource_identifier = parse_BIP122_uri(value)
    assert chain_id == HASH_A
    assert resource_type == expected_resource_type
    assert resource_identifier == HASH_B
