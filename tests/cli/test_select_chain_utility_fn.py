import pytest
import click
from click.testing import CliRunner

from populus.project import Project

from populus.utils.geth import (
    get_geth_ipc_path,
    get_data_dir as get_local_chain_datadir,
)
from populus.utils.cli import (
    select_chain,
)

from populus.api.config import (
    write_user_config,
)

@pytest.mark.parametrize(
    ('stdin,expected'),
    (
        ('0\n', '~~local_a~~'),
        ('1\n', '~~local_b~~'),
        ('2\n', '~~local_c~~'),
        ('3\n', '~~mainnet~~'),
        ('4\n', '~~ropsten~~'),
        ('5\n', '~~temp~~'),
        ('6\n', '~~tester~~'),
        ('7\n', '~~testrpc~~'),
        ('local_a\n', '~~local_a~~'),
        ('local_b\n', '~~local_b~~'),
        ('local_c\n', '~~local_c~~'),
        ('mainnet\n', '~~mainnet~~'),
        ('ropsten\n', '~~ropsten~~'),
        ('temp\n', '~~temp~~'),
        ('tester\n', '~~tester~~'),
        ('testrpc\n', '~~testrpc~~'),
    ),
)
def test_cli_select_chain_helper(project, user_config, user_config_path, stdin, expected):

    user_config['chains.local_a.chain.class'] = 'populus.chain.TesterChain'
    user_config['chains.local_a.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
    user_config['chains.local_a.web3.provider.settings.ipc_path'] = (
        get_geth_ipc_path(get_local_chain_datadir(project.project_root_dir, 'local_a'))
    )
    user_config['chains.local_b.chain.class'] = 'populus.chain.TesterChain'
    user_config['chains.local_b.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
    user_config['chains.local_b.web3.provider.settings.ipc_path'] = (
        get_geth_ipc_path(get_local_chain_datadir(project.project_root_dir, 'local_b'))
    )
    user_config['chains.local_c.chain.class'] = 'populus.chain.TesterChain'
    user_config['chains.local_c.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
    user_config['chains.local_c.web3.provider.settings.ipc_path'] = (
        get_geth_ipc_path(get_local_chain_datadir(project.project_root_dir, 'local_c'))
    )
    write_user_config(user_config, user_config_path)


    @click.command()
    def wrapper():
        chain_name = select_chain(user_config)
        print("~~{0}~~".format(chain_name))

    runner = CliRunner()
    result = runner.invoke(wrapper, [], input=stdin)

    assert result.exit_code == 0
    assert expected in result.output


@pytest.mark.parametrize(
    'stdin', ('local_a\n', '20\n'),
)
def test_cli_select_chain_helper_select_invalid_options(project, user_config, stdin):

    assert 'local_a' not in user_config['chains']
    assert len(user_config['chains']) < 20

    @click.command()
    def wrapper():
        chain_name = select_chain(user_config)
        print("~~{0}~~".format(chain_name))

    runner = CliRunner()
    result = runner.invoke(wrapper, [], input=stdin)

    assert result.exit_code != 0
