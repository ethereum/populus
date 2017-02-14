from populus.project import Project

from populus.utils.compat import (
    Timeout,
)


def test_external_rpc_chain(project_dir, write_project_file):
    project = Project()

    with project.get_chain('testrpc') as chain:
        web3 = chain.web3
        registrar = chain.registrar

        project.config['chains.external.chain.class'] = 'populus.chain.ExternalChain'
        project.config['chains.external.registrar'] = registrar.address
        project.config['chains.external.web3.provider.class'] = 'web3.providers.rpc.HTTPProvider'
        project.config['chains.external.web3.provider.settings.endpoint_uri'] = 'http://127.0.0.1:{0}'.format(chain.port)
        project.write_config()

        with project.get_chain('external') as external_chain:
            ext_web3 = external_chain.web3
            ext_registrar = external_chain.registrar

            assert ext_web3.eth.coinbase == web3.eth.coinbase
            assert registrar.address == ext_registrar.address


def test_external_ipc_chain(project_dir, write_project_file):
    project = Project()

    with project.get_chain('temp') as chain:
        web3 = chain.web3

        with Timeout(5) as timeout:
            while True:
                try:
                    chain.web3.eth.sendTransaction({
                        'from': chain.web3.eth.coinbase,
                        'to': chain.web3.eth.coinbase,
                        'value': 1
                    })
                except ValueError:
                    timeout.check()
                else:
                    break

        registrar = chain.registrar

        project.config['chains.external.chain.class'] = 'populus.chain.ExternalChain'
        project.config['chains.external.registrar'] = registrar.address
        project.config['chains.external.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
        project.config['chains.external.web3.provider.settings.ipc_path'] = chain.geth.ipc_path
        project.write_config()

        with project.get_chain('external') as external_chain:
            ext_web3 = external_chain.web3
            ext_registrar = external_chain.registrar

            assert ext_web3.eth.coinbase == web3.eth.coinbase
            assert registrar.address == ext_registrar.address
