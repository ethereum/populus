import pytest

import os
import json

from populus import Project
from populus.utils.config import (
    get_json_config_file_path,
)
from populus.utils.chains import (
    get_chain_definition,
)
from populus.utils.dependencies import (
    get_release_lockfile_path,
)
from populus.utils.packaging import (
    extract_package_metadata,
    load_release_lockfile,
    write_release_lockfile,
)
from populus.packages.installation import (
    write_installed_packages,
)


EXAMPLE_PACKAGES_BASE_PATH = './tests/example-packages'


@pytest.fixture()
def with_installed_packages_backend(project_dir):
    config_file_path = get_json_config_file_path(project_dir)
    config = {
        'version': '1',
        'chains': {
            'tester': {
                'chain': {'class': 'populus.chain.tester.TesterChain'},
                'web3': {'provider': {'class': 'web3.providers.tester.EthereumTesterProvider'}},
                'contracts': {
                    'backends': {
                        'InstalledPackages': {
                            "class": "populus.contracts.backends.installed_packages.InstalledPackagesBackend",
                            "priority": 10
                        }
                    }
                }
            }
        }
    }
    with open(config_file_path, 'w') as config_file:
        json.dump(config, config_file)
    return config_file_path


@pytest.yield_fixture()
def test_chain(project):
    project.config['chains.tester.contracts.backends'] = {
        'InstalledPackages': {'$ref': 'contracts.backends.InstalledPackages'},
        'Memory': {'$ref': 'contracts.backends.Memory'},
    }
    project.write_config()
    project.load_config()

    with project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def installed_safe_math_lib_dependency(populus_source_root,
                                       test_chain):
    chain = test_chain
    project = chain.project
    assert 'InstalledPackages' in chain.provider.provider_backends
    release_lockfile_path = os.path.join(
        populus_source_root,
        EXAMPLE_PACKAGES_BASE_PATH,
        'safe-math-lib',
        '1.0.0.json',
    )
    source_file_path = os.path.join(
        populus_source_root,
        EXAMPLE_PACKAGES_BASE_PATH,
        'safe-math-lib',
        'contracts',
        'SafeMathLib.sol',
    )
    release_lockfile = load_release_lockfile(release_lockfile_path)

    with open(source_file_path) as source_file:
        source_content = source_file.read()

    package_meta = extract_package_metadata(
        ('ipfs://QmfUwis9K2SLwnUh62PDb929JzU5J2aFKd4kS1YErYajdq',),
        release_lockfile,
    )
    package_data = {
        'meta': package_meta,
        'lockfile': release_lockfile,
        'source_tree': {'./contracts/SafeMathLib.sol': source_content},
        'dependencies': tuple(),
    }
    write_installed_packages(project.installed_packages_dir, [package_data])
    assert 'safe-math-lib' in project.installed_dependency_locations
    project._cached_compiled_contracts = None
    assert 'SafeMathLib' in project.compiled_contract_data


@pytest.fixture()
def deployed_safe_math_lib(test_chain, installed_safe_math_lib_dependency):
    chain = test_chain
    project = chain.project
    provider = chain.provider
    assert not provider.is_contract_available('SafeMathLib')

    release_lockfile_path = get_release_lockfile_path(
        project.installed_dependency_locations['safe-math-lib'],
    )

    release_lockfile = load_release_lockfile(release_lockfile_path)

    chain_definition = get_chain_definition(chain.web3)
    SafeMathLibFactory = provider.get_contract_factory('SafeMathLib')
    deploy_txn = SafeMathLibFactory.deploy()
    contract_address = chain.wait.for_contract_address(deploy_txn)
    release_lockfile['deployments'].update({
        chain_definition: {
            'SafeMathLib': {
                'address': contract_address,
                'contract_type': 'SafeMathLib',
                'runtime_bytecode': SafeMathLibFactory.bytecode_runtime,
            },
        }
    })
    write_release_lockfile(release_lockfile, release_lockfile_path)


def test_getting_contract_address_from_installed_package(test_chain,
                                                         deployed_safe_math_lib):
    chain = test_chain
    assert chain.provider.is_contract_available('SafeMathLib')
