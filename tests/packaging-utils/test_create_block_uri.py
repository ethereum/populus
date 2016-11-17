import pytest

from populus.utils.packaging import create_block_uri


@pytest.mark.parametrize(
    'chain_id,block_identifier,expected',
    (
        ('0x00', 0, 'blockchain://00/block/0'),
        ('00', 0, 'blockchain://00/block/0'),
        ('00', '0xabcd1234', 'blockchain://00/block/abcd1234'),
        ('00', 'abcd1234', 'blockchain://00/block/abcd1234'),
    )
)
def test_create_block_uri(chain_id, block_identifier, expected):
    actual = create_block_uri(chain_id, block_identifier)
    assert actual == expected
