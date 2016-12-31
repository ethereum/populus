import click
from click.testing import CliRunner

from geth.accounts import create_new_account

from populus.project import Project
from populus.utils.cli import (
    configure_chain,
)


def test_configuring_rpc_based_chain(project_dir):
    project = Project()

    @click.command()
    def wrapper():
        configure_chain(project, 'local')

    runner = CliRunner()
    result = runner.invoke(wrapper, [], input="\nrpc\n\n\n\n")

    assert result.exit_code == 0

    project.reload_config()

    chain_config = project.get_chain_config('local')
    assert chain_config['web3.provider.class'] == 'web3.providers.rpc.RPCProvider'


def test_configuring_ipc_based_chain(project_dir):
    project = Project()

    @click.command()
    def wrapper():
        configure_chain(project, 'local')

    runner = CliRunner()
    result = runner.invoke(wrapper, [], input="\nipc\n\n\n\n")

    assert result.exit_code == 0

    project.reload_config()

    chain_config = project.get_chain_config('local')
    assert chain_config['web3.provider.class'] == 'web3.providers.ipc.IPCProvider'
