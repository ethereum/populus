import pytest

import itertools
import json
import os

import jsonschema

from eth_utils import (
    to_dict,
)
from populus.utils.packaging import (
    validate_release_lockfile,
)

EXAMPLE_PACKAGES_BASE_PATH = './tests/example-packages'

EXAMPLE_RELEASE_LOCKFILES = (
    'owned/1.0.0.json',
    'transferable/1.0.0.json',
    'standard-token/1.0.0.json',
    'piper-coin/1.0.0.json',
    'safe-math-lib/1.0.0.json',
    'escrow/1.0.0.json',
    'wallet/1.0.0.json',
)


@pytest.mark.parametrize(
    'lockfile_path',
    EXAMPLE_RELEASE_LOCKFILES,
)
def test_example_release_lockfiles_are_valid(populus_source_root, lockfile_path):
    full_lockfile_path = os.path.join(
        populus_source_root,
        EXAMPLE_PACKAGES_BASE_PATH,
        lockfile_path,
    )
    with open(full_lockfile_path) as lockfile_file:
        release_lockfile = json.load(lockfile_file)

    validate_release_lockfile(release_lockfile)


MINIMAL_SCHEMA = {
    'lockfile_version': '1',
    'package_name': 'test-package',
    'version': '1.0.0',
}


@pytest.mark.parametrize(
    'release_lockfile',
    (
        MINIMAL_SCHEMA,
    ),
)
def test_example_release_lockfiles_are_valid(release_lockfile):
    validate_release_lockfile(release_lockfile)


DEFAULT_SCHEMA = {
    'lockfile_version': '1',
    'package_name': 'test-package',
    'version': '1.0.0',
}


@to_dict
def build_schema(**kwargs):
    for key in set(itertools.chain(DEFAULT_SCHEMA, kwargs)):
        if key in kwargs:
            if kwargs[key] is None:
                continue
            yield key, kwargs[key]
        else:
            yield key, DEFAULT_SCHEMA[key]


EMPTY_SCHEMA = {}
LOCKFILE_VERSION_AS_INTEGER = build_schema(lockfile_version=1)
LOCKFILE_VERSION_MISSING = build_schema(lockfile_version=None)
VERSION_MISSING = build_schema(version=None)
PACKAGE_NAME_MISSING = build_schema(package_name=None)
AUTHORS_AS_STRING = build_schema(meta={'authors': "Piper Merriam"})


@pytest.mark.parametrize(
    'release_lockfile',
    (
        EMPTY_SCHEMA,
        LOCKFILE_VERSION_AS_INTEGER,
        LOCKFILE_VERSION_MISSING,
        VERSION_MISSING,
        PACKAGE_NAME_MISSING,
        AUTHORS_AS_STRING,
    )
)
def test_raises_on_invalid_schema(release_lockfile):
    """
    TODO: This test suite could be greatly expanded as there are a lot more
    ways that lockfiles can be invalid.
    """
    with pytest.raises(jsonschema.ValidationError):
        validate_release_lockfile(release_lockfile)
