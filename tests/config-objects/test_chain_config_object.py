import pytest

from web3.providers.ipc import IPCProvider

from populus.chain import ExternalChain

from populus.config.chain import ChainConfig
from populus.config.web3 import Web3Config


def test_web3_config_property():
    chain_config = ChainConfig({
        'web3': {'provider': {'class': 'web3.providers.ipc.IPCProvider'}},
    })
    assert isinstance(chain_config.web3_config, Web3Config)
    assert chain_config.web3_config.provider_class is IPCProvider


def test_chain_class_property():
    chain_config = ChainConfig({
        'chain': {'class': 'populus.chain.ExternalChain'},
        'web3': {'provider': {'class': 'web3.providers.ipc.IPCProvider'}},
    })
    assert chain_config.chain_class is ExternalChain


def test_getting_chain_instance(project):
    chain_config = ChainConfig({
        'chain': {'class': 'populus.chain.ExternalChain'},
        'web3': {'provider': {'class': 'web3.providers.ipc.IPCProvider'}},
    })
    chain = chain_config.get_chain(project, 'test-chain')
    assert isinstance(chain, ExternalChain)
