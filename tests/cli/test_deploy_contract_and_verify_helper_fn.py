import pytest
import click
from click.testing import CliRunner

from geth.accounts import create_new_account

from populus.project import Project
from populus.utils.cli import (
    deploy_contract_and_verify,
)


def test_deploying_contract_with_successful_deploy(project_dir, MATH):
    project = Project()
    chain = project.get_chain('temp')

    assert False

    @click.command()
    def wrapper():
        account = deploy_contract_and_verify(chain)
        print("~~{0}~~".format(account))

    with chain:
        account = chain.web3.eth.accounts[account_index]

        runner = CliRunner()
        result = runner.invoke(wrapper, [], input="{0}\n".format(account_index))

    assert result.exit_code == 0
    expected = "~~{0}~~".format(account)
    assert expected in result.output
