import pytest

from web3.providers.ipc import IPCProvider

from populus.config.web3 import Web3Config


def test_provider_property_when_not_set():
    web3_config = Web3Config()

    with pytest.raises(KeyError):
        web3_config.provider


def test_provider_property_without_settings():
    web3_config = Web3Config({'provider': {'class': 'web3.providers.ipc.IPCProvider'}})
    assert isinstance(web3_config.provider, IPCProvider)


def test_provider_property_with_settings():
    web3_config = Web3Config({
        'provider': {
            'class': 'web3.providers.ipc.IPCProvider',
            'settings': {
                'ipc_path': '/not/a/real-path'
            },
        },
    })
    assert isinstance(web3_config.provider, IPCProvider)
    assert web3_config.provider.ipc_path == '/not/a/real-path'


def test_getting_web3_instance():
    web3_config = Web3Config({'provider': {'class': 'web3.providers.ipc.IPCProvider'}})
    web3 = web3_config.get_web3()

    assert isinstance(web3.currentProvider, IPCProvider)
