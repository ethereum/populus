import os
import pytest
import click
import shutil
from click.testing import CliRunner
import random
import gevent

from populus.utils.transactions import (
    wait_for_peers,
    wait_for_block_number,
)
from populus.utils.cli import (
    wait_for_sync,
)
from populus.project import Project


def test_request_account_unlock_with_correct_password(project_dir):
    project = Project()

    main_chain = project.get_chain('temp', nodiscover=False)
    sync_chain = project.get_chain('temp', mine=False, miner_threads=None)

    main_chain_data_dir = main_chain.geth.data_dir
    sync_chain_data_dir = sync_chain.geth.data_dir

    main_genesis_file = os.path.join(main_chain_data_dir, 'genesis.json')
    sync_genesis_file = os.path.join(sync_chain_data_dir, 'genesis.json')

    os.remove(sync_genesis_file)

    shutil.copyfile(main_genesis_file, sync_genesis_file)

    block_numbers = []

    runner = CliRunner()

    @click.command()
    def wrapper():
        block_numbers.append(sync_chain.web3.eth.blockNumber)
        wait_for_sync(sync_chain)
        block_numbers.append(sync_chain.web3.eth.blockNumber)

    with main_chain:
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

            wait_for_block_number(main_chain.web3, 5, 120)

            main_chain_start_block = main_chain.web3.eth.blockNumber
            sync_chain_start_block = sync_chain.web3.eth.blockNumber

            assert main_chain_start_block - sync_chain_start_block >= 5

            assert sync_chain.web3.net.peerCount == 0

            sync_chain.web3.admin.addPeer(main_enode)
            main_chain.web3.admin.addPeer(sync_enode)

            wait_for_peers(sync_chain.web3, timeout=30)

            result = runner.invoke(wrapper, [])

            assert result.exit_code == 0
            assert len(block_numbers) == 2
            import pdb; pdb.set_trace()
