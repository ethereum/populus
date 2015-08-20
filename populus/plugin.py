import os
import threading

import pytest


@pytest.fixture(scope="session")
def eth_coinbase():
    from ethereum import tester
    return tester.encode_hex(tester.accounts[0])


@pytest.yield_fixture()
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


@pytest.yield_fixture(scope="module")
def module_rpc_server():
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


@pytest.fixture(scope="session")
def rpc_client():
    from eth_rpc_client import Client
    client = Client('127.0.0.1', '8545')
    return client


@pytest.fixture(scope="module")
def contracts(request, rpc_client):
    from populus.utils import load_contracts
    from populus.contracts import Contract

    project_dir = getattr(request.module, "project_dir", os.getcwd())

    contracts = load_contracts(project_dir)

    contract_classes = {
        name: Contract(rpc_client, name, contract) for name, contract in contracts.items()
    }

    _dict = {
        '__iter__': lambda s: iter(contract_classes.items()),
        '__getitem__': lambda s, k: contract_classes.__getitem__[k],
    }
    _dict.update(contract_classes)

    return type('contracts', (object,), _dict)()


@pytest.fixture(scope="module")
def deployed_contracts(eth_coinbase, rpc_client, module_rpc_server, contracts):
    _dict = {}

    for contract_name, contract_class in contracts:
        txn_hash = contract_class.deploy(_from=eth_coinbase)
        txn_receipt = rpc_client.get_transaction_receipt(txn_hash)
        if txn_receipt is None:
            raise ValueError("Something is wrong?  transaction receipt was None")
        _dict[contract_name] = contract_class(txn_receipt['contractAddress'])

    return type('deployed_contracts', (object,), _dict)
