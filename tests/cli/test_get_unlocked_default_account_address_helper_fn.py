import pytest
import click
from click.testing import CliRunner

from geth.accounts import create_new_account

from populus.project import Project
from populus.utils.geth import (
    get_geth_ipc_path,
    get_data_dir as get_local_chain_datadir,
)
from populus.utils.cli import (
    get_unlocked_default_account_address,
)


@pytest.fixture()
def local_chain(project_dir):
    project = Project()
    project.config['chains.local.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
    project.config['chains.local.web3.provider.settings.ipc_path'] = (
        get_geth_ipc_path(get_local_chain_datadir(project.project_dir, 'local'))
    )
    project.write_config()

    chain = project.get_chain('local')

    # create a new account
    create_new_account(chain.geth.data_dir, b'a-test-password')

    return chain


def test_get_unlocked_default_account_address_with_no_config(local_chain):
    project = Project()
    chain = local_chain

    with chain:
        @click.command()
        def wrapper():
            account = get_unlocked_default_account_address(chain)
            print("~~{0}~~".format(account))

        runner = CliRunner()
        result = runner.invoke(wrapper, [], input="1\ny\na-test-password\n")

        default_account = chain.web3.eth.accounts[1]
        assert result.exit_code == 0, result.output + str(result.exception)
        expected = "~~{0}~~".format(default_account)
        assert expected in result.output

        project.reload_config()
        assert project.config['chains.local.web3.eth.default_account'] == default_account


def test_helper_fn_with_unlocked_pre_configured_account(local_chain):
    chain = local_chain
    project = chain.project

    with chain:
        web3 = chain.web3
        project.config['chains.local.web3.eth.default_account'] = web3.eth.coinbase
        project.write_config()

        @click.command()
        def wrapper():
            account = get_unlocked_default_account_address(chain)
            print("~~{0}~~".format(account))

        runner = CliRunner()
        result = runner.invoke(wrapper, [])

        assert result.exit_code == 0, result.output + str(result.exception)
        expected = "~~{0}~~".format(web3.eth.coinbase)
        assert expected in result.output

        project.reload_config()
        assert project.config['chains.local.web3.eth.default_account'] == web3.eth.coinbase


def test_helper_fn_with_locked_pre_configured_account(local_chain):
    chain = local_chain
    project = chain.project

    with chain:
        web3 = chain.web3
        project.config['chains.local.web3.eth.default_account'] = web3.eth.accounts[1]
        project.write_config()

        @click.command()
        def wrapper():
            account = get_unlocked_default_account_address(chain)
            print("~~{0}~~".format(account))

        runner = CliRunner()
        result = runner.invoke(wrapper, [], input="a-test-password\n")

        assert result.exit_code == 0, result.output + str(result.exception)
        expected = "~~{0}~~".format(web3.eth.accounts[1])
        assert expected in result.output

        project.reload_config()
        assert project.config['chains.local.web3.eth.default_account'] == web3.eth.accounts[1]
