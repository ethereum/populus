from populus.project import Project
from populus.utils.transactions import (
    wait_for_unlock,
)


def test_external_rpc_chain(project_dir, write_project_file):
    project = Project()

    with project.get_chain('testrpc') as chain:
        web3 = chain.web3
        registrar = chain.registrar

        ini_contents = '\n'.join((
            "[chain:external]",
            "is_external=True",
            "provider=web3.providers.rpc.RPCProvider",
            "port={port}".format(port=chain.port),
            "registrar={registrar}".format(registrar=registrar.address),
        ))
        write_project_file('populus.ini', ini_contents)

        project.reload_config()

        with project.get_chain('external') as external_chain:
            ext_web3 = external_chain.web3
            ext_registrar = external_chain.registrar

            assert ext_web3.eth.coinbase == web3.eth.coinbase
            assert registrar.address == ext_registrar.address


def test_external_ipc_chain(project_dir, write_project_file):
    project = Project()

    with project.get_chain('temp') as chain:
        web3 = chain.web3
        wait_for_unlock(web3, timeout=30)
        registrar = chain.registrar

        ini_contents = '\n'.join((
            "[chain:external]",
            "is_external=True",
            "ipc_path={ipc_path}".format(ipc_path=chain.geth.ipc_path),
            "registrar={registrar}".format(registrar=registrar.address),
        ))
        write_project_file('populus.ini', ini_contents)

        project.reload_config()

        with project.get_chain('external') as external_chain:
            ext_web3 = external_chain.web3
            ext_registrar = external_chain.registrar

            assert ext_web3.eth.coinbase == web3.eth.coinbase
            assert registrar.address == ext_registrar.address
