from flaky import flaky

from populus.utils.transactions import (
    wait_for_block_number,
)
from populus.chain import (
    TESTNET_BLOCK_1_HASH,
    MAINNET_BLOCK_1_HASH,
)
from populus.project import (
    Project,
)


@flaky
def test_project_tester_chain(project_dir):
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


@flaky
def test_project_morden_chain(project_dir):
    project = Project()

    chain = project.get_chain('morden')

    with chain as running_morden_chain:
        web3 = running_morden_chain.web3
        assert web3.version.node.startswith('Geth')

        wait_for_block_number(web3, 1, 180)

        block_1 = web3.eth.getBlock(1)
        assert block_1['hash'] == TESTNET_BLOCK_1_HASH


@flaky
def test_project_local_chain_ipc(project_dir, write_project_file):
    write_project_file('populus.ini', '\n'.join((
        '[chain:custom-chain]',
        'provider=web3.providers.ipc.IPCProvider',
    )))
    project = Project()

    chain = project.get_chain('custom-chain')

    with chain as running_local_chain:
        web3 = running_local_chain.web3
        assert web3.version.node.startswith('Geth')

        wait_for_block_number(web3, 1, 180)

        block_1 = web3.eth.getBlock(1)
        assert block_1['hash'] != MAINNET_BLOCK_1_HASH
        assert block_1['hash'] != TESTNET_BLOCK_1_HASH
        assert block_1['miner'] == web3.eth.coinbase


@flaky
def test_project_local_chain_rpc(project_dir, write_project_file):
    write_project_file('populus.ini', '\n'.join((
        '[chain:custom-chain]',
        'provider=web3.providers.rpc.RPCProvider',
    )))
    project = Project()

    chain = project.get_chain('custom-chain')

    with chain as running_local_chain:
        web3 = running_local_chain.web3
        assert web3.version.node.startswith('Geth')

        wait_for_block_number(web3, 1, 180)

        block_1 = web3.eth.getBlock(1)
        assert block_1['hash'] != MAINNET_BLOCK_1_HASH
        assert block_1['hash'] != TESTNET_BLOCK_1_HASH
        assert block_1['miner'] == web3.eth.coinbase
