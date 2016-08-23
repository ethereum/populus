import pytest
from flaky import flaky
import click
from click.testing import CliRunner

from geth.accounts import create_new_account

from populus.project import Project
from populus.utils.cli import (
    get_unlocked_deploy_from_address,
)


@pytest.fixture()
def local_chain(project_dir, write_project_file):
    write_project_file('populus.ini', '[chain:local]')

    project = Project()
    chain = project.get_chain('local')

    # create a new account
    create_new_account(chain.geth.data_dir, b'a-test-password')

    return chain


@flaky
def test_get_unlocked_deploy_from_address_with_no_config(local_chain):
    project = Project()
    chain = local_chain

    with chain:
        @click.command()
        def wrapper():
            account = get_unlocked_deploy_from_address(chain)
            print("~~{0}~~".format(account))

        runner = CliRunner()
        result = runner.invoke(wrapper, [], input="1\ny\na-test-password\n")

        deploy_from = chain.web3.eth.accounts[1]
        assert result.exit_code == 0
        expected = "~~{0}~~".format(deploy_from)
        assert expected in result.output

        project.reload_config()
        assert project.config.chains['local']['deploy_from'] == deploy_from


@flaky
def test_helper_fn_with_unlocked_pre_configured_account(local_chain):
    chain = local_chain
    project = chain.project

    with chain:
        web3 = chain.web3
        project.config.set('chain:local', 'deploy_from', web3.eth.coinbase)
        project.write_config()
        project.reload_config()

        @click.command()
        def wrapper():
            account = get_unlocked_deploy_from_address(chain)
            print("~~{0}~~".format(account))

        runner = CliRunner()
        result = runner.invoke(wrapper, [])

        assert result.exit_code == 0
        expected = "~~{0}~~".format(web3.eth.coinbase)
        assert expected in result.output

        project.reload_config()
        assert project.config.chains['local']['deploy_from'] == web3.eth.coinbase


@flaky
def test_helper_fn_with_locked_pre_configured_account(local_chain):
    chain = local_chain
    project = chain.project

    with chain:
        web3 = chain.web3
        project.config.set('chain:local', 'deploy_from', web3.eth.accounts[1])
        project.write_config()

        @click.command()
        def wrapper():
            account = get_unlocked_deploy_from_address(chain)
            print("~~{0}~~".format(account))

        runner = CliRunner()
        result = runner.invoke(wrapper, [], input="a-test-password\n")

        assert result.exit_code == 0
        expected = "~~{0}~~".format(web3.eth.accounts[1])
        assert expected in result.output

        project.reload_config()
        assert project.config.chains['local']['deploy_from'] == web3.eth.accounts[1]
