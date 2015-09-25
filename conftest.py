import pytest


@pytest.fixture(params=["ethtester", "rpc"])
def blockchain_client(request):
    if request.param == "ethtester":
        from populus.ethtester_client import EthTesterClient
        return EthTesterClient()
    elif request.param == 'rpc':
        from eth_rpc_client import Client
        rpc_host = getattr(request.module, 'rpc_server_host', '127.0.0.1')
        rpc_port = getattr(request.module, 'rpc_server_port', 8545)
        return Client(rpc_host, rpc_port)
    else:
        raise ValueError("What happened!")
