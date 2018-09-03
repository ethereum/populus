import pytest

from web3.providers.ipc import IPCProvider

from populus.chain import (
    LocalGethChain,
    ExternalChain,
    TesterChain as _TesterChain,
    TemporaryGethChain,
    MainnetChain,
    TestnetChain as _TestnetChain,
)

from populus.config.chain import ChainConfig
from populus.config.web3 import Web3Config


def test_web3_config_property():
    chain_config = ChainConfig({
        'web3': {'provider': {'class': 'web3.providers.ipc.IPCProvider'}},
    })
    assert isinstance(chain_config.get_web3_config(), Web3Config)
    assert chain_config.get_web3_config().provider_class is IPCProvider


def test_chain_class_property():
    chain_config = ChainConfig({
        'chain': {'class': 'populus.chain.external.ExternalChain'},
        'web3': {'provider': {'class': 'web3.providers.ipc.IPCProvider'}},
    })
    assert chain_config.chain_class is ExternalChain


def test_getting_chain_instance(project):
    chain_config = ChainConfig({
        'chain': {'class': 'populus.chain.external.ExternalChain'},
        'web3': {'provider': {'class': 'web3.providers.ipc.IPCProvider'}},
    })
    chain = chain_config.get_chain(project, 'test-chain')
    assert isinstance(chain, ExternalChain)


@pytest.mark.parametrize(
    'value,expected',
    (
        ('local', 'populus.chain.geth.LocalGethChain'),
        ('external', 'populus.chain.external.ExternalChain'),
        ('tester', 'populus.chain.tester.TesterChain'),
        ('temp', 'populus.chain.geth.TemporaryGethChain'),
        ('mainnet', 'populus.chain.geth.MainnetChain'),
        ('testnet', 'populus.chain.geth.TestnetChain'),
        ('ropsten', 'populus.chain.geth.TestnetChain'),
        ('populus.chain.geth.LocalGethChain', 'populus.chain.geth.LocalGethChain'),
        ('populus.chain.external.ExternalChain', 'populus.chain.external.ExternalChain'),
        ('populus.chain.tester.TesterChain', 'populus.chain.tester.TesterChain'),
        ('populus.chain.geth.TemporaryGethChain', 'populus.chain.geth.TemporaryGethChain'),
        ('populus.chain.geth.MainnetChain', 'populus.chain.geth.MainnetChain'),
        ('populus.chain.geth.TestnetChain', 'populus.chain.geth.TestnetChain'),
        (LocalGethChain, 'populus.chain.geth.LocalGethChain'),
        (ExternalChain, 'populus.chain.external.ExternalChain'),
        (_TesterChain, 'populus.chain.tester.TesterChain'),
        (TemporaryGethChain, 'populus.chain.geth.TemporaryGethChain'),
        (MainnetChain, 'populus.chain.geth.MainnetChain'),
        (_TestnetChain, 'populus.chain.geth.TestnetChain'),
    ),
    ids=(
        # shorthand strings
        'local-shorthand',
        'external-shorthand',
        'tester-shorthand',
        'temp-shorthand',
        'mainnet-shorthand',
        'testnet-shorthand',
        'ropsten-shorthand',
        # python paths
        'local-pythonpath',
        'external-pythonpath',
        'tester-pythonpath',
        'temp-pythonpath',
        'mainnet-pythonpath',
        'testnet-pythonpath',
        # classes
        'local-classobj',
        'external-classobj',
        'tester-classobj',
        'temp-classobj',
        'mainnet-classobj',
        'testnet-classobj',
    ),
)
def test_set_chain_class_api(value, expected):
    chain_config = ChainConfig()
    chain_config.set_chain_class(value)
    assert chain_config['chain.class'] == expected


def test_is_external_property():
    chain_config = ChainConfig()
    chain_config.set_chain_class('local')
    assert chain_config.is_external is False
    chain_config.set_chain_class('external')
    assert chain_config.is_external is True
