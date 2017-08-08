import pytest

from populus.utils.ipfs import is_ipfs_uri


@pytest.mark.parametrize(
    'value,expected',
    (
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', True),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', True),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', True),
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', True),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', True),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', True),
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', True),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', True),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', True),
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', True),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', True),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', True),
        # malformed
        ('ipfs//QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('ipfs/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('ipfsQmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        # HTTP
        ('http://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        ('https://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        # No hash
        ('ipfs://', False),
    )
)
def test_is_ipfs_uri(value, expected):
    actual = is_ipfs_uri(value)
    assert actual is expected
