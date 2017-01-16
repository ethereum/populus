from populus.project import Project


def test_external_rpc_chain(project_dir, write_project_file):
    project = Project()

    with project.get_chain('testrpc') as chain:
        web3 = chain.web3
        registrar = chain.store.registrar

        project.config['chains.external.is_external'] = True
        project.config['chains.external.web3.provider.class'] = 'web3.providers.rpc.RPCProvider'
        project.config['chains.external.web3.provider.settings.rpc_port'] = chain.rpc_port
        project.config['chains.external.contracts.backends'] = {
            "JSONFile": {
                "$ref": "contracts.backends.JSONFile"
            }
        }

        project.write_config()

        with project.get_chain('external') as external_chain:
            ext_web3 = external_chain.web3

            assert ext_web3.eth.coinbase == web3.eth.coinbase


def test_external_ipc_chain(project_dir, write_project_file):
    project = Project()

    with project.get_chain('temp') as chain:
        web3 = chain.web3
        chain.wait.for_unlock(timeout=30)

        project.config['chains.external.is_external'] = True
        project.config['chains.external.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
        project.config['chains.external.web3.provider.settings.ipc_path'] = chain.geth.ipc_path
        project.config['chains.external.contracts.backends'] = {
            "JSONFile": {
                "$ref": "contracts.backends.JSONFile"
            }
        }
        project.write_config()

        with project.get_chain('external') as external_chain:
            ext_web3 = external_chain.web3

            assert ext_web3.eth.coinbase == web3.eth.coinbase
