import pytest


@pytest.fixture(autouse=True)
def project_contracts(project_dir, write_project_file, MATH_SOURCE):
    write_project_file('contracts/Math.sol', MATH_SOURCE)


def test_contracts_fixture(contracts, project_dir, write_project_file, MATH):

    assert contracts.Math
    assert contracts.Math.code == MATH['code']
    assert contracts.Math.code_runtime == MATH['code_runtime']
    assert contracts.Math.abi == MATH['abi']
