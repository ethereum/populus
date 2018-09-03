import pytest

from web3.providers.ipc import (
    IPCProvider,
)
from web3.providers.rpc import (
    HTTPProvider,
)

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


@pytest.mark.parametrize(
    'value,expected',
    (
        ('ipc', 'web3.providers.ipc.IPCProvider'),
        ('rpc', 'web3.providers.rpc.HTTPProvider'),
        ('web3.providers.ipc.IPCProvider', 'web3.providers.ipc.IPCProvider'),
        ('web3.providers.rpc.HTTPProvider', 'web3.providers.rpc.HTTPProvider'),
        (
            'web3.providers.websocket.WebsocketProvider',
            'web3.providers.websocket.WebsocketProvider'
        ),
        (IPCProvider, 'web3.providers.ipc.IPCProvider'),
        (HTTPProvider, 'web3.providers.rpc.HTTPProvider'),
    ),
    ids=(
        'ipc-shorthand',
        'rpc-shorthand',
        'ipc-pythonpath',
        'http-pythonpath',
        'rpc-pythonpath',
        'ipc-classobj',
        'http-classobj',
    )
)
def test_set_provider_class_api(value, expected):
    web3_config = Web3Config()
    web3_config.set_provider_class(value)
    assert web3_config['provider.class'] == expected


def test_provider_kwargs_property():
    web3_config = Web3Config({
        'provider': {
            'class': 'web3.providers.ipc.IPCProvider',
        },
    })
    assert web3_config.provider_kwargs == {}

    web3_config.provider_kwargs = {'ipc_path': '/not/a/real-path'}
    assert web3_config.provider_kwargs == {'ipc_path': '/not/a/real-path'}

    web3_config.provider_kwargs['some-key'] = 32
    assert web3_config.provider_kwargs == {'ipc_path': '/not/a/real-path', 'some-key': 32}


def test_getting_web3_instance():
    web3_config = Web3Config({'provider': {'class': 'web3.providers.ipc.IPCProvider'}})
    web3 = web3_config.get_web3()

    assert isinstance(web3.providers[0], IPCProvider)


def test_default_account_property():
    web3_config = Web3Config()

    with pytest.raises(KeyError):
        web3_config.default_account

    web3_config.default_account = '0x0000000000000000000000000000000000000001'
    assert web3_config.default_account == '0x0000000000000000000000000000000000000001'
