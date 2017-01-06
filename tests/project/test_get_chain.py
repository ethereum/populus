import pytest

from flaky import flaky

from populus.chain import (
    TESTNET_BLOCK_1_HASH,
    MAINNET_BLOCK_1_HASH,
)
from populus.project import (
    Project,
)
from populus.utils.chains import (
    get_geth_ipc_path,
    get_data_dir as get_local_chain_datadir,
)
from populus.utils.networking import (
    get_open_port,
)


@flaky
def test_project_tester_chain(project_dir):
    project = Project()

    chain = project.get_chain('tester')

    with chain as running_tester_chain:
        web3 = running_tester_chain.web3
        assert web3.version.node.startswith('TestRPC')


@flaky
def test_project_testrpc_chain(project_dir):
    project = Project()

    chain = project.get_chain('testrpc')

    with chain as running_tester_chain:
        web3 = running_tester_chain.web3
        assert web3.version.node.startswith('TestRPC')


@flaky
def test_project_temp_chain(project_dir):
    project = Project()

    chain = project.get_chain('temp')

    with chain as running_temp_chain:
        web3 = running_temp_chain.web3
        assert hasattr(running_temp_chain, 'geth')
        assert web3.version.node.startswith('Geth')


#@flaky
@pytest.mark.skip("Morden no longer exists")
def test_project_morden_chain(project_dir):
    project = Project()

    chain = project.get_chain('morden')

    with chain as running_morden_chain:
        web3 = running_morden_chain.web3
        assert web3.version.node.startswith('Geth')

        running_morden_chain.wait.for_block(block_number=1, timeout=180)

        block_1 = web3.eth.getBlock(1)
        assert block_1['hash'] == TESTNET_BLOCK_1_HASH


@flaky
def test_project_local_chain_ipc(project_dir):
    project = Project()

    ipc_path = get_geth_ipc_path(get_local_chain_datadir(project.project_dir, 'local'))

    project.config['chains.local.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
    project.config['chains.local.web3.provider.settings.ipc_path'] = ipc_path
    project.write_config()

    chain = project.get_chain('local')

    with chain as running_local_chain:
        web3 = running_local_chain.web3
        assert web3.version.node.startswith('Geth')

        running_local_chain.wait.for_block(block_number=1, timeout=180)

        block_1 = web3.eth.getBlock(1)
        assert block_1['hash'] != MAINNET_BLOCK_1_HASH
        assert block_1['hash'] != TESTNET_BLOCK_1_HASH
        assert block_1['miner'] == web3.eth.coinbase


@flaky
def test_project_local_chain_rpc(project_dir):
    project = Project()
    rpc_port = str(get_open_port())
    project.config['chains.local.web3.provider.class'] = 'web3.providers.rpc.RPCProvider'
    project.config['chains.local.geth.settings.rpc_port'] = rpc_port
    project.config['chains.local.web3.settings.rpc_port'] = rpc_port
    project.write_config()

    chain = project.get_chain('local')

    with chain as running_local_chain:
        web3 = running_local_chain.web3
        assert web3.version.node.startswith('Geth')

        running_local_chain.wait.for_block(block_number=1, timeout=180)

        block_1 = web3.eth.getBlock(1)
        assert block_1['hash'] != MAINNET_BLOCK_1_HASH
        assert block_1['hash'] != TESTNET_BLOCK_1_HASH
        assert block_1['miner'] == web3.eth.coinbase
