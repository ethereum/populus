import pytest

from web3.providers.ipc import IPCProvider

from populus.chain import (
    LocalGethChain,
    ExternalChain,
    TesterChain,
    TestRPCChain,
    TemporaryGethChain,
    MainnetChain,
    TestnetChain,
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


@pytest.mark.parametrize(
    'value,expected',
    (
        ('local', 'populus.chain.LocalGethChain'),
        ('external', 'populus.chain.ExternalChain'),
        ('tester', 'populus.chain.TesterChain'),
        ('testrpc', 'populus.chain.TestRPCChain'),
        ('temp', 'populus.chain.TemporaryGethChain'),
        ('mainnet', 'populus.chain.MainnetChain'),
        ('testnet', 'populus.chain.TestnetChain'),
        ('ropsten', 'populus.chain.TestnetChain'),
        ('populus.chain.LocalGethChain', 'populus.chain.LocalGethChain'),
        ('populus.chain.ExternalChain', 'populus.chain.ExternalChain'),
        ('populus.chain.TesterChain', 'populus.chain.TesterChain'),
        ('populus.chain.TestRPCChain', 'populus.chain.TestRPCChain'),
        ('populus.chain.TemporaryGethChain', 'populus.chain.TemporaryGethChain'),
        ('populus.chain.MainnetChain', 'populus.chain.MainnetChain'),
        ('populus.chain.TestnetChain', 'populus.chain.TestnetChain'),
        (LocalGethChain, 'populus.chain.LocalGethChain'),
        (ExternalChain, 'populus.chain.ExternalChain'),
        (TesterChain, 'populus.chain.TesterChain'),
        (TestRPCChain, 'populus.chain.TestRPCChain'),
        (TemporaryGethChain, 'populus.chain.TemporaryGethChain'),
        (MainnetChain, 'populus.chain.MainnetChain'),
        (TestnetChain, 'populus.chain.TestnetChain'),
    )
)
def test_set_chain_class_api(value, expected):
    chain_config = ChainConfig()
    chain_config.set_chain_class(value)
    assert chain_config['chain.class'] == expected
