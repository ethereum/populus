import pytest

import os

from populus.config import Config
from populus.contracts.exceptions import NoKnownAddress
from populus.contracts.backends.filesystem import (
    JSONFileBackend,
    load_registrar_data,
)

from populus.utils.chains import (
    check_if_chain_matches_chain_uri,
)


FILE_NAME = './registrar.json'


@pytest.fixture
def backend_config():
    return Config({
        'file_path': FILE_NAME,
    })


@pytest.fixture
def backend(project_dir, chain, backend_config):
    return JSONFileBackend(chain, backend_config)


def test_is_provider_and_registrar_by_default(project_dir, chain, backend_config):
    backend = JSONFileBackend(chain, backend_config)
    assert backend.is_provider is False
    assert backend.is_registrar is True


def test_setting_an_address(project_dir, backend, web3):
    backend.set_contract_address('some-key', '0xd3cda913deb6f67967b99d67acdfa1712c293601')

    with open(os.path.join(project_dir, FILE_NAME)) as registrar_file:
        registrar_data = load_registrar_data(registrar_file)

    chain_definitions = registrar_data['deployments']
    assert len(chain_definitions) == 1
    chain_definition = tuple(chain_definitions.keys())[0]

    is_match = check_if_chain_matches_chain_uri(web3, chain_definition)
    assert is_match is True

    contract_addresses = chain_definitions[chain_definition]
    assert 'some-key' in contract_addresses
    assert contract_addresses['some-key'] == '0xd3cda913deb6f67967b99d67acdfa1712c293601'


def test_getting_an_address(project_dir, backend, web3):
    backend.set_contract_address('some-key', '0xd3cda913deb6f67967b99d67acdfa1712c293601')

    addresses = backend.get_contract_addresses('some-key')
    assert len(addresses) == 1
    address = addresses[0]
    assert address == '0xd3cda913deb6f67967b99d67acdfa1712c293601'


def test_getting_an_unknown_address(project_dir, backend, web3):
    with pytest.raises(NoKnownAddress):
        backend.get_contract_addresses('some-key')
