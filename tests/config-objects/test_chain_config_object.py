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
        ('testrpc', 'populus.chain.testrpc.TestRPCChain'),
        ('temp', 'populus.chain.geth.TemporaryGethChain'),
        ('mainnet', 'populus.chain.geth.MainnetChain'),
        ('testnet', 'populus.chain.geth.TestnetChain'),
        ('ropsten', 'populus.chain.geth.TestnetChain'),
        ('populus.chain.geth.LocalGethChain', 'populus.chain.geth.LocalGethChain'),
        ('populus.chain.external.ExternalChain', 'populus.chain.external.ExternalChain'),
        ('populus.chain.tester.TesterChain', 'populus.chain.tester.TesterChain'),
        ('populus.chain.testrpc.TestRPCChain', 'populus.chain.testrpc.TestRPCChain'),
        ('populus.chain.geth.TemporaryGethChain', 'populus.chain.geth.TemporaryGethChain'),
        ('populus.chain.geth.MainnetChain', 'populus.chain.geth.MainnetChain'),
        ('populus.chain.geth.TestnetChain', 'populus.chain.geth.TestnetChain'),
        (LocalGethChain, 'populus.chain.geth.LocalGethChain'),
        (ExternalChain, 'populus.chain.external.ExternalChain'),
        (TesterChain, 'populus.chain.tester.TesterChain'),
        (TestRPCChain, 'populus.chain.testrpc.TestRPCChain'),
        (TemporaryGethChain, 'populus.chain.geth.TemporaryGethChain'),
        (MainnetChain, 'populus.chain.geth.MainnetChain'),
        (TestnetChain, 'populus.chain.geth.TestnetChain'),
    )
)
def test_set_chain_class_api(value, expected):
    chain_config = ChainConfig()
    chain_config.set_chain_class(value)
    assert chain_config['chain.class'] == expected
