from populus.utils.packaging import (
    extract_package_identifiers_from_dependencies,
)


DEPENDENCIES = {
    'owned-1': '1.0.0',
    'owned-2': '>2.0.0',
    'owned-3': '>=3.0.0',
    'owned-4': '<4.0.0',
    'owned-5': '<=5.0.0',
    'owned-6': 'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
}
EXPECTED_DEPENDENCIES = {
    'owned-1==1.0.0',
    'owned-2>2.0.0',
    'owned-3>=3.0.0',
    'owned-4<4.0.0',
    'owned-5<=5.0.0',
    'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
}


def test_extract_package_identifiers_from_dependencies():
    actual_dependencies = extract_package_identifiers_from_dependencies(DEPENDENCIES)
    assert set(actual_dependencies) == EXPECTED_DEPENDENCIES
