import pytest

from populus.utils.packaging import (
    construct_package_identifier,
)


@pytest.mark.parametrize(
    'dependency_name,dependency_identifier,expected',
    (
        ("owned", "1.0.0", "owned==1.0.0"),
        ("owned", ">1.0.0", "owned>1.0.0"),
        ("owned", ">=1.0.0", "owned>=1.0.0"),
        ("powned", "owned==1.0.0", "powned:owned==1.0.0"),
        (
            'owned',
            'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND',
            'owned@ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND',
        ),
    )
)
def test_construct_package_identifier(dependency_name, dependency_identifier, expected):
    actual = construct_package_identifier(dependency_name, dependency_identifier)
    assert actual == expected
