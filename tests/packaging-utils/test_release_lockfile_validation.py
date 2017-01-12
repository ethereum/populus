import pytest

import json
import os

import jsonschema

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


@pytest.mark.parametrize(
    'release_lockfile',
    (
        {},
    )
)
def test_raises_on_invalid_schema(release_lockfile):
    with pytest.raises(jsonschema.ValidationError):
        validate_release_lockfile(release_lockfile)
