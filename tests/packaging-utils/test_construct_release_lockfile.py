import pytest

import json

from populus.packages.build import (
    construct_release_lockfile,
)


TEST_CONTRACT_SOURCE = """pragma solidity ^0.4.0;

contract TestContract {
    uint value;

    function readValue() constant returns (uint) {
        return value;
    }

    function setValue(uint _value) public {
        value = _value;
    }
}
"""


@pytest.fixture()
def TestContract(project_dir, write_project_file):
    write_project_file('contracts/TestContract.sol', TEST_CONTRACT_SOURCE)


@pytest.fixture()
def package_manifest(project):
    _package_manifest = {
        'package_name': 'test-package',
        'version': '1.0.0',
    }
    with open(project.package_manifest_path, 'w') as package_manifest_file:
        json.dump(_package_manifest, package_manifest_file)

    return _package_manifest


def test_requires_a_package_manifest(project, TestContract):
    assert not project.has_package_manifest

    with pytest.raises(ValueError):
        construct_release_lockfile(project, [], [], ['TestContract'])


def test_simple_lockfile_with_only_sources(project, TestContract, package_manifest, mock_package_backends):
    project.package_backends = mock_package_backends
    release_lockfile = construct_release_lockfile(project, [], [], [])

    assert 'version' in release_lockfile
    assert release_lockfile['version'] == '1.0.0'

    # no meta information present so key should be excluded
    assert 'meta' not in release_lockfile

    assert 'sources' in release_lockfile
    sources = release_lockfile['sources']
    assert './contracts/TestContract.sol' in sources
    assert sources['./contracts/TestContract.sol'] == 'ipfs://QmTRxTJ7LLYjKuC6toWFBAKu3h7rXxEzmsV19TyQ4q5RzF'

    assert 'contract_types' not in release_lockfile
