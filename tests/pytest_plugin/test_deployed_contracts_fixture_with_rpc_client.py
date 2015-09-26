import os


project_dir = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'projects', 'test-02',
)
deploy_client_type = 'rpc'


def test_deployed_contracts_fixture_with_ethtester(rpc_server, deployed_contracts):
    math = deployed_contracts.Math
    assert math.add.call(11, 12) == 23
    assert math.multiply7.call(11) == 77
    assert math.return13.call() == 13
