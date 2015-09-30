import pytest


@pytest.fixture(params=["ethtester", "rpc"])
def blockchain_client(request, ethtester_client, rpc_client):
    if request.param == "ethtester":
        return ethtester_client
    elif request.param == 'rpc':
        return rpc_client
    else:
        raise ValueError("What happened!")
