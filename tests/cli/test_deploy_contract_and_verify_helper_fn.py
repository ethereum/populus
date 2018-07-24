import click
from click.testing import CliRunner

from populus.utils.cli import (
    deploy_contract_and_verify,
)
from populus.utils.testing import load_contract_fixture


@load_contract_fixture('Math.sol')
def test_deploying_contract_with_successful_deploy(project):
    chain = project.get_chain('tester')

    exports = []

    with chain:
        Math = chain.provider.get_contract_factory('Math')

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


@load_contract_fixture('Math.sol')
def test_with_successful_deploy_sans_runtime_bytecode(project):
    chain = project.get_chain('tester')

    exports = []

    with chain:
        Math = chain.provider.get_contract_factory('Math')

        Math.bytecode_runtime = None
        assert Math.bytecode_runtime is None

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


@load_contract_fixture('ThrowsInConstructor.sol')
def test_deploying_contract_with_error_during_deploy(project):
    chain = project.get_chain('tester')

    exports = []

    with chain:
        ThrowsInConstructor = chain.provider.get_contract_factory('ThrowsInConstructor')

        @click.command()
        def wrapper():
            thrower_contract = deploy_contract_and_verify(
                chain,
                contract_name='ThrowsInConstructor',
                ContractFactory=ThrowsInConstructor,
                deploy_args=[True],
            )
            exports.append(thrower_contract)
            print("~~{0}~~".format(thrower_contract.address))

        runner = CliRunner()
        result = runner.invoke(wrapper, [])

    assert result.exit_code != 0
    assert not exports


@load_contract_fixture('ThrowsInConstructor.sol')
def test_deploying_contract_with_error_during_deploy_sanity_check(project):
    """
    Just a sanity check that the `Thrower` contract can be successfully
    deployed.
    """
    chain = project.get_chain('tester')

    exports = []

    with chain:
        ThrowsInConstructor = chain.provider.get_contract_factory('ThrowsInConstructor')

        @click.command()
        def wrapper():
            math_contract = deploy_contract_and_verify(
                chain,
                contract_name='ThrowsInConstructor',
                ContractFactory=ThrowsInConstructor,
                deploy_args=[False],
            )
            exports.append(math_contract)
            print("~~{0}~~".format(math_contract.address))

        runner = CliRunner()
        result = runner.invoke(wrapper, [])

    assert result.exit_code == 0
    assert exports
    assert "Verified contract bytecode" in result.output
    assert "No runtime available" not in result.output
