from populus.client import Client


def test_get_coinbase(rpc_server):
    client = Client('127.0.0.1', '8545')
    cb = client.get_coinbase()

    assert cb == '0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1'
