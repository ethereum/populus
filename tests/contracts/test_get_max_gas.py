from populus.contracts import get_max_gas


def test_getting_max_gas(rpc_client, rpc_server):
    max_gas = get_max_gas(rpc_client)
    assert max_gas == 950000000
