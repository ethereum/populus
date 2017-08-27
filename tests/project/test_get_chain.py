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

from populus.chain.helpers import (
    get_chain,
)

TESTNET_BLOCK_1_HASH = '0xad47413137a753b2061ad9b484bf7b0fc061f654b951b562218e9f66505be6ce'
MAINNET_BLOCK_1_HASH = '0x88e96d4537bea4d9c05d12549907b32561d3bf31f45aae734cdc119f13406cb6'


@pytest.mark.slow
def test_project_tester_chain(project, user_config):

    chain = get_chain('tester', user_config, chain_dir=project.project_root_dir)

    with chain as running_tester_chain:
        web3 = running_tester_chain.web3
        assert web3.version.node.startswith('TestRPC')


@pytest.mark.slow
def test_project_testrpc_chain(project, user_config):

    chain = get_chain('testrpc', user_config, chain_dir=project.project_root_dir)

    with chain as running_tester_chain:
        web3 = running_tester_chain.web3
        assert web3.version.node.startswith('TestRPC')
