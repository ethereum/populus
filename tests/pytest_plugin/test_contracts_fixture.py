import os


project_dir = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'projects', 'test-02',
)


def test_contracts_fixture(contracts):
    assert contracts.Math
    assert hasattr(contracts.Math, 'add')
    assert hasattr(contracts.Math, 'multiply7')
    assert hasattr(contracts.Math, 'return13')
