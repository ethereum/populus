import pytest


@pytest.mark.slow
def test_external_rpc_chain(project):
    with project.get_chain('testrpc') as chain:
        web3 = chain.web3

        project.config['chains.external.chain.class'] = 'populus.chain.ExternalChain'
        project.config['chains.external.web3.provider.class'] = 'web3.providers.rpc.HTTPProvider'
        project.config['chains.external.web3.provider.settings.endpoint_uri'] = 'http://127.0.0.1:{0}'.format(chain.rpc_port)
        project.config['chains.external.contracts.backends.Memory'] = {'$ref': 'contracts.backends.Memory'}
        project.write_config()

        with project.get_chain('external') as external_chain:
            ext_web3 = external_chain.web3

            assert ext_web3.eth.coinbase == web3.eth.coinbase


@pytest.mark.slow
def test_external_ipc_chain(project, wait_for_unlock):
    with project.get_chain('temp') as chain:
        web3 = chain.web3
        registrar = chain.registrar

        wait_for_unlock(web3)

        project.config['chains.external.chain.class'] = 'populus.chain.ExternalChain'
        project.config['chains.external.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
        project.config['chains.external.web3.provider.settings.ipc_path'] = chain.geth.ipc_path
        project.config['chains.external.contracts.backends.Memory'] = {'$ref': 'contracts.backends.Memory'}
        project.write_config()

        with project.get_chain('external') as external_chain:
            ext_web3 = external_chain.web3

            assert ext_web3.eth.coinbase == web3.eth.coinbase
