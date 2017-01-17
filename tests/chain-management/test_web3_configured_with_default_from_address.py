from populus import Project


def test_chain_web3_is_preconfigured_with_default_from(project_dir):
    project = Project()

    default_account = '0x0000000000000000000000000000000000001234'
    project.config['web3.Tester.eth.default_account'] = default_account

    with project.get_chain('tester') as chain:
        web3 = chain.web3

        assert web3.eth.defaultAccount == default_account
        assert web3.eth.coinbase != default_account
