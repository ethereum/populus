import pytest

from populus.utils.ipfs import (
    generate_file_hash,
)


@pytest.mark.parametrize(
    "file_name,file_contents,expected",
    (
        ("test-1.txt", "piper\n", "QmUdxEGxvp71kqYLkA91mtNg9QRRSPBtA3UV6VuYhoP7DB"),
        ("test-2.txt", "pipermerriam\n", "QmXqrQR7EMePe9LCRUVrfkxYg5EHRNpcA1PZnN4AnbM9DW"),
        ("test-3.txt", "this is a test file for ipfs hash generation\n", "QmYknNUKXWSaxfCWVgHd8uVCYHhzPerVCLvCCBedWtqbnv"),
    ),
)
def test_generate_file_hash(project_dir, write_project_file, file_name, file_contents, expected):
    write_project_file(file_name, file_contents)
    ipfs_multihash = generate_file_hash(file_name)
    assert ipfs_multihash == expected
