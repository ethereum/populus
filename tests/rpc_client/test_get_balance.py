from populus.client import Client


def test_get_balance(rpc_server, eth_tester):
    client = Client('127.0.0.1', '8545')
    balance = client.get_balance(eth_tester.encode_hex(eth_tester.accounts[0]))

    assert balance == 1000000000000000000000000L
