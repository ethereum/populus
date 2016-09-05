import os
import click
import shutil
from click.testing import CliRunner
from flaky import flaky

from populus.utils.networking import (
    get_open_port,
)
from populus.utils.cli import (
    show_chain_sync_progress,
)
from populus.project import Project


BLOCK_DELTA = int(os.environ.get('CHAIN_SYNC_BLOCK_DELTA', '40'))


@flaky(max_runs=3)
def test_show_chain_sync_progress():
    project = Project()

    main_chain = project.get_chain('temp',
                                   no_discover=False,
                                   max_peers=None,
                                   port=str(get_open_port()),
                                   rpc_enabled=False,
                                   ws_enabled=False)
    with main_chain:
        sync_chain = project.get_chain('temp',
                                       no_discover=False,
                                       max_peers=None,
                                       mine=False,
                                       miner_threads=None,
                                       port=str(get_open_port()),
                                       rpc_enabled=False,
                                       ws_enabled=False)

        main_chain_data_dir = main_chain.geth.data_dir
        sync_chain_data_dir = sync_chain.geth.data_dir

        main_genesis_file = os.path.join(main_chain_data_dir, 'genesis.json')
        sync_genesis_file = os.path.join(sync_chain_data_dir, 'genesis.json')

        main_chaindata_dir = os.path.join(main_chain_data_dir, 'chaindata')
        sync_chaindata_dir = os.path.join(sync_chain_data_dir, 'chaindata')

        os.remove(sync_genesis_file)
        shutil.rmtree(sync_chaindata_dir)

        shutil.copyfile(main_genesis_file, sync_genesis_file)
        shutil.copytree(main_chaindata_dir, sync_chaindata_dir)

        block_numbers = []

        runner = CliRunner()

        @click.command()
        def wrapper():
            block_numbers.append(sync_chain.web3.eth.blockNumber)
            show_chain_sync_progress(sync_chain)
            block_numbers.append(sync_chain.web3.eth.blockNumber)

        with sync_chain:
            main_node_info = main_chain.web3.admin.nodeInfo
            main_enode = "enode://{node_id}@127.0.0.1:{node_port}".format(
                node_id=main_node_info['id'],
                node_port=main_node_info['ports']['listener'],
            )
            sync_node_info = sync_chain.web3.admin.nodeInfo
            sync_enode = "enode://{node_id}@127.0.0.1:{node_port}".format(
                node_id=sync_node_info['id'],
                node_port=sync_node_info['ports']['listener'],
            )

            chain.wait.for_block_number(BLOCK_DELTA, timeout=BLOCK_DELTA * 4)

            main_chain_start_block = main_chain.web3.eth.blockNumber
            sync_chain_start_block = sync_chain.web3.eth.blockNumber

            assert main_chain_start_block - sync_chain_start_block >= BLOCK_DELTA // 2

            assert sync_chain.web3.net.peerCount == 0

            sync_chain.web3.admin.addPeer(main_enode)
            main_chain.web3.admin.addPeer(sync_enode)

            chain.wait.for_peers(timeout=60)

            result = runner.invoke(wrapper, [])

            assert result.exit_code == 0
            assert len(block_numbers) == 2

            start_block = block_numbers[0]
            end_block = block_numbers[1]

            assert start_block <= 1
            assert end_block >= 20
