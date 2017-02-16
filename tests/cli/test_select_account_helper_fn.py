import pytest
import click
from click.testing import CliRunner

from geth.accounts import create_new_account

from populus.project import Project
from populus.utils.cli import (
    select_account,
)


@pytest.mark.slow
@pytest.mark.parametrize(
    ('account_index'),
    (0, 1),
)
def test_select_account_helper_with_indexes(project_dir, account_index):
    project = Project()
    chain = project.get_chain('temp')

    # create 3 new accounts
    create_new_account(chain.geth.data_dir, b'a-test-password')


    @click.command()
    def wrapper():
        account = select_account(chain)
        print("~~{0}~~".format(account))

    with chain:
        account = chain.web3.eth.accounts[account_index]

        runner = CliRunner()
        result = runner.invoke(wrapper, [], input="{0}\n".format(account_index))

    assert result.exit_code == 0
    expected = "~~{0}~~".format(account)
    assert expected in result.output


@pytest.mark.slow
@pytest.mark.parametrize(
    ('account_index'),
    (0, 1),
)
def test_select_account_helper_with_accounts(project_dir, account_index):
    project = Project()
    chain = project.get_chain('temp')

    # create 3 new accounts
    create_new_account(chain.geth.data_dir, b'a-test-password')


    @click.command()
    def wrapper():
        account = select_account(chain)
        print("~~{0}~~".format(account))

    with chain:
        account = chain.web3.eth.accounts[account_index]

        runner = CliRunner()
        result = runner.invoke(wrapper, [], input="{0}\n".format(account))

    assert result.exit_code == 0
    expected = "~~{0}~~".format(account)
    assert expected in result.output


@pytest.mark.slow
@pytest.mark.parametrize(
    ('stdin'),
    (20, '0xd3cda913deb6f67967b99d67acdfa1712c293601'),
)
def test_select_account_with_invalid_option(project_dir, stdin):
    project = Project()
    chain = project.get_chain('temp')

    @click.command()
    def wrapper():
        account = select_account(chain)
        print("~~{0}~~".format(account))

    with chain:
        runner = CliRunner()
        result = runner.invoke(wrapper, [], input="{0}\n".format(stdin))

    assert result.exit_code != 0
