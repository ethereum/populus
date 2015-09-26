from eth_rpc_client import Client


deploy_client_type = 'rpc'


def test_deploy_client_as_rpc_client(deploy_client):
    assert isinstance(deploy_client, Client)
