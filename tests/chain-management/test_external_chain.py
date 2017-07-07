import pytest

from web3.providers.tester import EthereumTesterProvider


def test_external_chain(project):
    project.config['chains.external.chain.class'] = 'populus.chain.ExternalChain'
    project.config['chains.external.web3.provider.class'] = 'web3.providers.tester.EthereumTesterProvider'
    project.config['chains.external.contracts.backends.Memory'] = {'$ref': 'contracts.backends.Memory'}
    project.write_config()

    with project.get_chain('external') as external_chain:
        assert isinstance(external_chain.web3.currentProvider, EthereumTesterProvider)
