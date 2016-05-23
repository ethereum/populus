from eth_tester_client import EthTesterClient


deploy_client_type = 'ethtester'


def test_deploy_client_as_ethtester(deploy_client):
    assert isinstance(deploy_client, EthTesterClient)
