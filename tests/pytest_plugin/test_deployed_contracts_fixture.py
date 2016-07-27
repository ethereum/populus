import pytest


@pytest.fixture(autouse=True)
def project_contracts(project_dir, write_project_file, MATH_SOURCE):
    write_project_file('contracts/Math.sol', MATH_SOURCE)


def test_deployed_contracts_fixture_with_ethtester(deployed_contracts):
    math = deployed_contracts.Math
    assert math.address

    assert math.call().add(11, 12) == 23
    assert math.call().multiply7(11) == 77
    assert math.call().return13() == 13
