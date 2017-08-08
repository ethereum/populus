import pytest

import json

from populus.utils.packaging import (
    extract_dependency_name_from_identifier_lineage,
)


@pytest.mark.parametrize(
    'lineage,expected',
    (
        (("owned>=1.0.0", "owned==1.0.0", "ipfs://Qm.."), "owned"),
        (("owned", "owned==1.0.0", "ipfs://Qm.."), "owned"),
        (("owned==1.0.0", "ipfs://Qm.."), "owned"),
        (("ipfs://Qm..",), "fallback"),
        (("powned:owned>=1.0.0", "owned>=1.0.0", "owned==1.0.0", "ipfs://Qm.."), "powned"),
        (("powned:owneg", "owned", "owned==1.0.0", "ipfs://Qm.."), "powned"),
        (("powned:owned==1.0.0", "owned==1.0.0", "ipfs://Qm.."), "powned"),
        (("powned@ipfs://Qm..", "ipfs://Qm..",), "powned"),
        ((".", "owned>=1.0.0", "owned==1.0.0", "ipfs://Qm.."), "owned"),
        ((".", "owned", "owned==1.0.0", "ipfs://Qm.."), "owned"),
        ((".", "owned==1.0.0", "ipfs://Qm.."), "owned"),
        ((".", "ipfs://Qm..",), "fallback"),
        ((".", "powned:owned>=1.0.0", "owned>=1.0.0", "owned==1.0.0", "ipfs://Qm.."), "powned"),
        ((".", "powned:owneg", "owned", "owned==1.0.0", "ipfs://Qm.."), "powned"),
        ((".", "powned:owned==1.0.0", "owned==1.0.0", "ipfs://Qm.."), "powned"),
        ((".", "powned@ipfs://Qm..", "ipfs://Qm..",), "powned"),
        (("./test-package-1.0.0.json",), "fallback"),
        (("test-package@./test-package-1.0.0.json",), "test-package"),
    )
)
def test_extract_dependency_name_from_identifier_lineage(project_dir,
                                                         write_project_file,
                                                         lineage,
                                                         expected):
    write_project_file("test-package-1.0.0.json", json.dumps({
        "lockfile_version": "1",
        "package_name": "test-package",
        "version": "1.0.0",
    }))
    release_lockfile = {'package_name': 'fallback'}
    actual = extract_dependency_name_from_identifier_lineage(lineage, release_lockfile)
    assert actual == expected
