import pytest

from web3.providers.tester import EthereumTesterProvider

from populus.chain.helpers import (
    get_chain,
)

from populus.api.config import (
    write_user_config,
)

def test_external_chain(project, user_config, user_config_path):

    user_config['chains.external.chain.class'] = 'populus.chain.ExternalChain'
    user_config['chains.external.web3.provider.class'] = 'web3.providers.tester.EthereumTesterProvider'
    user_config['chains.external.contracts.backends.Memory'] = {'$ref': 'contracts.backends.Memory'}
    write_user_config(user_config, user_config_path)

    with get_chain("external", user_config, chain_dir=project.project_root_dir) as external_chain:
        assert isinstance(external_chain.web3.currentProvider, EthereumTesterProvider)
