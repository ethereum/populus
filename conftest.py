import threading

import pytest


@pytest.fixture
def eth_tester():
    from ethereum import tester
    return tester


@pytest.yield_fixture(scope="session")
def rpc_server():
    from testrpc.__main__ import create_server
    from testrpc.testrpc import evm_reset

    server = create_server('127.0.0.1', 8545)

    evm_reset()

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    yield server

    server.shutdown()
    server.server_close()
