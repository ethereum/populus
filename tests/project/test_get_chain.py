import pytest

from populus.project import (
    Project,
)

from populus.utils.geth import (
    get_geth_ipc_path,
    get_data_dir as get_local_chain_datadir,
)
from populus.utils.networking import (
    get_open_port,
)


@pytest.mark.slow
def test_project_tester_chain(project_dir):
    project = Project()

    chain = project.get_chain('tester')

    with chain as running_tester_chain:
        web3 = running_tester_chain.web3
        assert web3.version.node.startswith('TestRPC')


@pytest.mark.slow
def test_project_testrpc_chain(project_dir):
    project = Project()

    chain = project.get_chain('testrpc')

    with chain as running_tester_chain:
        web3 = running_tester_chain.web3
        assert web3.version.node.startswith('TestRPC')
