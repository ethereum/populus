import pytest
import click
from click.testing import CliRunner

from geth.accounts import create_new_account

from populus.project import Project
from populus.utils.cli import (
    configure_chain,
)


@pytest.mark.parametrize(
    ('stdin,expected_config'),
    (
        ("\nipc\n\n\n", {'provider': 'web3.providers.ipc.IPCProvider'}),
        ("\nrpc\n\n\n\n", {'provider': 'web3.providers.rpc.RPCProvider'}),
    )
)
def test_select_account_helper_with_indexes(project_dir,
                                            write_project_file,
                                            stdin,
                                            expected_config):
    write_project_file('populus.ini', '[chain:local]')
    project = Project()

    @click.command()
    def wrapper():
        configure_chain(project, 'local')

    runner = CliRunner()
    result = runner.invoke(wrapper, [], input=stdin)

    assert result.exit_code == 0

    project.reload_config()

    chain_config = project.config.chains['local']
    for key, value in expected_config.items():
        assert key in chain_config
        assert chain_config[key] == value
