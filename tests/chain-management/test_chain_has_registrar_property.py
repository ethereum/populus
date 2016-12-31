from populus import Project

from populus.utils.chains import (
    get_geth_ipc_path,
    get_data_dir as get_local_chain_datadir,
)


def test_testrpc_chain_has_registrar(project_dir):
    project = Project()

    with project.get_chain('testrpc') as chain:
        assert chain.has_registrar is True


def test_tester_chain_has_registrar(project_dir):
    project = Project()

    with project.get_chain('tester') as chain:
        assert chain.has_registrar is True


def test_temp_chain_has_registrar(project_dir):
    project = Project()

    with project.get_chain('temp') as chain:
        assert chain.has_registrar is True


def test_geth_chain_has_registrar(project_dir, write_project_file):
    project = Project()
    project.config['chains.local.registrar'] = 'faking-it'
    project.config['chains.local.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
    project.config['chains.local.web3.provider.settings.ipc_path'] = (
        get_geth_ipc_path(get_local_chain_datadir(project.project_dir, 'local'))
    )

    with project.get_chain('local') as chain:
        assert chain.has_registrar is True
