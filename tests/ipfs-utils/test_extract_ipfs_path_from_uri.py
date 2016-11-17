import pytest

from populus.utils.ipfs import extract_ipfs_path_from_uri


@pytest.mark.parametrize(
    'value,expected',
    (
        (
            'ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
        ),
        (
            'ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
        ),
        (
            'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
        ),
        (
            'ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
        ),
        (
            'ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
        ),
        (
            'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
        ),
        (
            'ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
        ),
        (
            'ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
        ),
        (
            'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
        ),
        (
            'ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
        ),
        (
            'ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
        ),
        (
            'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
        ),
    )
)
def test_extract_ipfs_path_from_uri(value, expected):
    actual = extract_ipfs_path_from_uri(value)
    assert actual == expected

