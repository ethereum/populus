from web3.providers.eth_tester import (
    EthereumTesterProvider,
)


def test_external_chain(project):
    project.config['chains.external.chain.class'] = 'populus.chain.ExternalChain'
    project.config['chains.external.web3.provider.class'] = 'web3.providers.eth_tester.EthereumTesterProvider'  # noqa: E501
    project.config['chains.external.contracts.backends.Memory'] = {'$ref': 'contracts.backends.Memory'}  # noqa: E501

    with project.get_chain('external') as external_chain:
        assert isinstance(external_chain.web3.providers[0], EthereumTesterProvider)
