from geth.accounts import create_new_account

from web3.utils.string import force_text

from populus.project import Project


def test_chain_web3_is_preconfigured_with_default_from(project_dir):
    default_account = '0x0000000000000000000000000000000000000001'
    project = Project()
    project.config['chains.local.web3.provider.class'] = 'web3.providers.tester.EthereumTesterProvider'
    project.config['chains.local.web3.eth.default_account'] = default_account

    with project.get_chain('local') as chain:
        web3 = chain.web3

        assert web3.eth.defaultAccount == default_account
        assert web3.eth.coinbase != default_account
