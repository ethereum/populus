import pytest

from populus.utils.ipfs import create_ipfs_uri


@pytest.mark.parametrize(
    'value,expected',
    (
        ('QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', 'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u'),
        ('QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', 'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme'),
    )
)
def test_create_ipfs_uri(value, expected):
    actual = create_ipfs_uri(value)
    assert actual == expected
