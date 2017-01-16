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
    chain = project.get_chain('testrpc')

    exports = []

    with chain:
        Math = chain.web3.eth.contract(**MATH)
        @click.command()
        def wrapper():
            math_contract = deploy_contract_and_verify(
                chain,
                contract_name='Math',
                ContractFactory=Math,
            )
            exports.append(math_contract)
            print("~~{0}~~".format(math_contract.address))

        runner = CliRunner()
        result = runner.invoke(wrapper, [])

    assert result.exit_code == 0, str(result.output) + '\n' + str(result.exception)
    assert len(exports) == 1
    math_contract = exports[0]
    expected = "~~{0}~~".format(math_contract.address)
    assert expected in result.output
    # ensure that we actually did bytecode verification
    assert "Verified contract bytecode" in result.output
    assert "No runtime available" not in result.output


def test_with_successful_deploy_sans_runtime_bytecode(project_dir,
                                                      MATH):
    project = Project()
    chain = project.get_chain('testrpc')

    exports = []

    with chain:
        Math = chain.web3.eth.contract(
            abi=MATH['abi'],
            code=MATH['code'],
        )
        assert not Math.code_runtime

        @click.command()
        def wrapper():
            math_contract = deploy_contract_and_verify(
                chain,
                contract_name='Math',
                ContractFactory=Math,
            )
            exports.append(math_contract)
            print("~~{0}~~".format(math_contract.address))

        runner = CliRunner()
        result = runner.invoke(wrapper, [])

    assert result.exit_code == 0, str(result.output) + '\n' + str(result.exception)
    assert len(exports) == 1
    math_contract = exports[0]
    expected = "~~{0}~~".format(math_contract.address)
    assert expected in result.output
    assert "Verified contract bytecode" not in result.output
    assert "No runtime available" in result.output


def test_deploying_contract_with_error_during_deploy(project_dir, THROWER):
    project = Project()
    chain = project.get_chain('testrpc')

    exports = []

    with chain:
        Thrower = chain.web3.eth.contract(**THROWER)
        @click.command()
        def wrapper():
            math_contract = deploy_contract_and_verify(
                chain,
                contract_name='Thrower',
                ContractFactory=Thrower,
                deploy_arguments=[True],
            )
            exports.append(math_contract)
            print("~~{0}~~".format(math_contract.address))

        runner = CliRunner()
        result = runner.invoke(wrapper, [])

    assert result.exit_code != 0


def test_deploying_contract_with_error_during_deploy_sanity_check(project_dir,
                                                                  THROWER):
    """
    Just a sanity check that the `Thrower` contract can be successfully
    deployed.
    """
    project = Project()
    chain = project.get_chain('testrpc')

    exports = []

    with chain:
        Thrower = chain.web3.eth.contract(**THROWER)
        @click.command()
        def wrapper():
            math_contract = deploy_contract_and_verify(
                chain,
                contract_name='Thrower',
                ContractFactory=Thrower,
                deploy_arguments=[False],
            )
            exports.append(math_contract)
            print("~~{0}~~".format(math_contract.address))

        runner = CliRunner()
        result = runner.invoke(wrapper, [])

    assert result.exit_code == 0
    assert "Verified contract bytecode" in result.output
    assert "No runtime available" not in result.output
