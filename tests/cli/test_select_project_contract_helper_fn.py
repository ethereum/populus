import pytest
import click
from click.testing import CliRunner

from populus.project import Project
from populus.utils.cli import (
    select_project_contract,
)


@pytest.mark.parametrize(
    ('input, expected_name'),
    (
        (0, 'A'),
        (1, 'B'),
        (2, 'C'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    )
)
def test_select_project_contract_helper(project_dir,
                                        write_project_file,
                                        input,
                                        expected_name):
    write_project_file('contracts/ContractA.sol', 'contract A { function A() {}}')
    write_project_file('contracts/ContractB.sol', 'contract B { function B() {}}')
    write_project_file('contracts/ContractC.sol', 'contract C { function C() {}}')

    project = Project()

    assert 'A' in project.compiled_contract_data
    assert 'B' in project.compiled_contract_data
    assert 'C' in project.compiled_contract_data

    @click.command()
    def wrapper():
        contract_name = select_project_contract(project)
        print("~~{0}~~".format(contract_name))

    runner = CliRunner()
    result = runner.invoke(wrapper, [], input="{0}\n".format(input))

    assert result.exit_code == 0
    expected = "~~{0}~~".format(expected_name)
    assert expected in result.output


@pytest.mark.parametrize(
    ('input'),
    (3, 'D'),
)
def test_select_project_contract_helper(project_dir,
                                        write_project_file,
                                        input):
    write_project_file('contracts/ContractA.sol', 'contract A { function A() {}}')
    write_project_file('contracts/ContractB.sol', 'contract B { function B() {}}')
    write_project_file('contracts/ContractC.sol', 'contract C { function C() {}}')

    project = Project()

    assert 'A' in project.compiled_contract_data
    assert 'B' in project.compiled_contract_data
    assert 'C' in project.compiled_contract_data

    @click.command()
    def wrapper():
        contract_name = select_project_contract(project)
        print("~~{0}~~".format(contract_name))

    runner = CliRunner()
    result = runner.invoke(wrapper, [], input="{0}\n".format(input))

    assert result.exit_code == 1
