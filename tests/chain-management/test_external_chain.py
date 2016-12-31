from populus.project import Project


def test_external_rpc_chain(project_dir, write_project_file):
    project = Project()

    with project.get_chain('testrpc') as chain:
        web3 = chain.web3
        registrar = chain.registrar

        project.config['chains.external.is_external'] = True
        project.config['chains.external.registrar'] = registrar.address
        project.config['chains.external.web3.provider.class'] = 'web3.providers.rpc.RPCProvider'
        project.config['chains.external.web3.provider.settings.rpc_port'] = chain.port
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
        chain.wait.for_unlock(timeout=30)
        registrar = chain.registrar

        project.config['chains.external.is_external'] = True
        project.config['chains.external.registrar'] = registrar.address
        project.config['chains.external.web3.provider.class'] = 'web3.providers.rpc.IPCProvider'
        project.config['chains.external.web3.provider.settings.ipc_path'] = chain.geth.ipc_path
        project.write_config()

        with project.get_chain('external') as external_chain:
            ext_web3 = external_chain.web3
            ext_registrar = external_chain.registrar

            assert ext_web3.eth.coinbase == web3.eth.coinbase
            assert registrar.address == ext_registrar.address
