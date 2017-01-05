import pytest

from populus.utils.ipfs import (
    generate_ipfs_multihash,
)


@pytest.mark.parametrize(
    "file_contents,expected",
    (
        ("piper\n", "QmUdxEGxvp71kqYLkA91mtNg9QRRSPBtA3UV6VuYhoP7DB"),
    ),
)
def test_generate_ipfs_multihash(file_contents, expected):
    ipfs_multihash = generate_ipfs_multihash(file_contents)
    assert ipfs_multihash == expected
