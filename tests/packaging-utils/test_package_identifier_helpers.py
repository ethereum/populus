import itertools

import pytest

from populus.utils.packaging import(
    is_package_name,
    is_direct_package_identifier,
    is_aliased_package_identifier,
    is_aliased_ipfs_uri,
    parse_package_identifier,
)


NAME_ONLY_IDENTIFIERS = (
    'populus',
    'with-12345',
    'with-dash',
)


ALIASED_NAME_ONLY_IDENTIFIERS = tuple(
    ':'.join(('alias-' + name, name)) for name in NAME_ONLY_IDENTIFIERS
)


EXACT_VERSION_IDENTIFIERS = (
    'populus==1.0.0',
    # Names with versions and prerelease
    'populus==1.0.0-beta1',
    'populus==1.0.0-b1',
    'populus==1.0.0-beta1.other2',
    'populus==1.0.0-beta1.other2.another',
    # Names with versions and build
    'populus==1.0.0+d4feab1',
    'populus==1.0.0+d4feab1.deadbeef',
    # Names with versions and prerelease and build
    'populus==1.0.0-beta1+d4feab1',
    'populus==1.0.0-beta1.another2+d4feab1.deadbeef',
)


ALIASED_EXACT_VERSION_IDENTIFIERS = tuple(
    ':'.join((parse_package_identifier(name)[0], name)) for name in EXACT_VERSION_IDENTIFIERS
)


COMPARISON_IDENTIFIERS = (
    'populus>=1.0.0',
    'populus<=1.0.0',
    'populus>1.0.0',
    'populus<1.0.0',
)


ALIASED_COMPARISON_IDENTIFIERS = tuple(
    ':'.join((parse_package_identifier(name)[0], name)) for name in COMPARISON_IDENTIFIERS
)


BAD_NAMES = (
    '-dash-start',
    '0-number-start',
    'with_underscore',
    'withCapital',
)


ALIASED_BAD_NAMES = tuple(
    ':'.join((name, name)) for name in BAD_NAMES
)


BAD_NAMES_WITH_VERSIONS = (
    '-dash-start==1.0.0',
    '0-number-start==1.0.0',
    'with_underscore==1.0.0',
    'withCapital==1.0.0',
)


ALIASED_BAD_NAMES_WITH_VERSIONS = tuple(
    ':'.join((name.partition('==')[0], name)) for name in BAD_NAMES_WITH_VERSIONS
)


@pytest.mark.parametrize(
    'value,expected',
    tuple(
        zip(NAME_ONLY_IDENTIFIERS, itertools.repeat(True))
    ) + tuple(
        zip(ALIASED_NAME_ONLY_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(EXACT_VERSION_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(ALIASED_EXACT_VERSION_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(COMPARISON_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(ALIASED_COMPARISON_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(BAD_NAMES, itertools.repeat(False))
    ) + tuple(
        zip(ALIASED_BAD_NAMES, itertools.repeat(False))
    )
)
def test_is_package_name(value, expected):
    actual = is_package_name(value)
    assert actual is expected


@pytest.mark.parametrize(
    'value,expected',
    tuple(
        zip(NAME_ONLY_IDENTIFIERS, itertools.repeat(True))
    ) + tuple(
        zip(ALIASED_NAME_ONLY_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(EXACT_VERSION_IDENTIFIERS, itertools.repeat(True))
    ) + tuple(
        zip(ALIASED_EXACT_VERSION_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(COMPARISON_IDENTIFIERS, itertools.repeat(True))
    ) + tuple(
        zip(ALIASED_COMPARISON_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(BAD_NAMES, itertools.repeat(False))
    ) + tuple(
        zip(ALIASED_BAD_NAMES, itertools.repeat(False))
    )
)
def test_is_direct_package_identifier(value, expected):
    actual = is_direct_package_identifier(value)
    assert actual is expected


@pytest.mark.parametrize(
    'value,expected',
    tuple(
        zip(NAME_ONLY_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(ALIASED_NAME_ONLY_IDENTIFIERS, itertools.repeat(True))
    ) + tuple(
        zip(EXACT_VERSION_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(ALIASED_EXACT_VERSION_IDENTIFIERS, itertools.repeat(True))
    ) + tuple(
        zip(COMPARISON_IDENTIFIERS, itertools.repeat(False))
    ) + tuple(
        zip(ALIASED_COMPARISON_IDENTIFIERS, itertools.repeat(True))
    ) + tuple(
        zip(BAD_NAMES, itertools.repeat(False))
    ) + tuple(
        zip(ALIASED_BAD_NAMES, itertools.repeat(False))
    )
)
def test_is_aliased_package_identifier(value, expected):
    actual = is_aliased_package_identifier(value)
    assert actual is expected


@pytest.mark.parametrize(
    'value,expected',
    (
        ('populus', ('populus', None, None)),
    )
)
def test_parse_package_identifier(value, expected):
    name, comparison, version = parse_package_identifier(value)
    assert (name, comparison, version) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        # Not Aliased
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', False),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', False),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', False),
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', False),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', False),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', False),
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        # malformed
        ('ipfs//QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('ipfs/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('ipfsQmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        # HTTP
        ('http://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        ('https://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        # No hash
        ('ipfs://', False),
        # Aliased Identifiers
        ('populus@ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', True),
        ('populus@ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', True),
        ('populus@ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', True),
        ('populus@ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', True),
        ('populus@ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', True),
        ('populus@ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', True),
        ('populus@ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', True),
        ('populus@ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', True),
        ('populus@ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', True),
        ('populus@ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', True),
        ('populus@ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', True),
        ('populus@ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', True),
        # malformed
        ('populus@ipfs//QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('populus@ipfs/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('populus@ipfsQmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        # HTTP
        ('populus@http://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        ('populus@https://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        # No hash
        ('populus@ipfs://', False),
        # Aliased with bad package names
        ('-starts-with-dash@ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', False),
        ('has_underscore@ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', False),
        ('hasCapitalCase@ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', False),
    )
)
def test_is_aliased_ipfs_uri(value, expected):
    actual = is_aliased_ipfs_uri(value)
    assert actual is expected
