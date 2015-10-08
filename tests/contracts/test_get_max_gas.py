from populus.contracts import get_max_gas


def test_getting_max_gas(blockchain_client, testrpc_server):
    max_gas = get_max_gas(blockchain_client)
    assert abs(max_gas - 950000000) < 10000000
