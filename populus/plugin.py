import os
import time
import threading
import signal

import pytest


@pytest.fixture(scope="session")
def test_coinbase():
    from ethereum import tester
    return tester.encode_hex(tester.accounts[0])


@pytest.yield_fixture(scope="module")
def geth_node(request):
    from populus.geth import (
        run_geth_node,
        get_geth_data_dir,
        ensure_account_exists,
        reset_chain,
    )
    from populus.utils import (
        ensure_path_exists,
        wait_for_popen,
    )

    project_dir = getattr(request.module, 'geth_project_dir', os.getcwd())
    chain_name = getattr(request.module, 'geth_chain_name', 'default-test')
    data_dir = get_geth_data_dir(project_dir, chain_name)

    ensure_path_exists(data_dir)
    ensure_account_exists(data_dir)

    if getattr(request.module, 'geth_reset_chain', True):
        reset_chain(data_dir)

    rpc_port = getattr(request.module, 'rpc_port', '8545')
    rpc_host = getattr(request.module, 'rpc_host', '127.0.0.1')

    command, proc = run_geth_node(data_dir, rpc_addr=rpc_host, rpc_port=rpc_port)

    start = time.time()
    while time.time() < start + 5:
        line = proc.get_stderr_nowait()
        if line and 'Starting mining operation' in line:
            break
    else:
        raise ValueError("Geth process never started")

    yield proc
    if proc.poll():
        proc.send_signal(signal.SIGINT)
        wait_for_popen(proc, 5)
    if proc.poll():
        proc.terminate()
        wait_for_popen(proc, 2)
    if proc.poll():
        proc.kill()
        wait_for_popen(proc, 1)


@pytest.fixture(scope='module')
def geth_coinbase(request):
    from populus.geth import (
        get_geth_data_dir,
        ensure_account_exists,
    )
    from populus.utils import (
        ensure_path_exists,
    )

    project_dir = getattr(request.module, 'project_dir', os.getcwd())
    chain_name = getattr(request.module, 'chain_name', 'default-test')
    data_dir = get_geth_data_dir(project_dir, chain_name)

    ensure_path_exists(data_dir)
    geth_coinbase = ensure_account_exists(data_dir)
    return geth_coinbase


@pytest.yield_fixture()
def rpc_server(request):
    from testrpc.__main__ import create_server
    from testrpc.testrpc import evm_reset

    rpc_port = getattr(request.module, 'rpc_port', 8545)
    rpc_host = getattr(request.module, 'rpc_host', '127.0.0.1')

    server = create_server(rpc_host, rpc_port)

    evm_reset()

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    yield server

    server.shutdown()
    server.server_close()


@pytest.fixture(scope="module")
def rpc_client(request):
    from eth_rpc_client import Client
    rpc_hostname = getattr(request.module, 'rpc_server_host', '127.0.0.1')
    rpc_port = getattr(request.module, 'rpc_server_port', '8545')
    client = Client(rpc_hostname, rpc_port)
    return client


@pytest.fixture(scope="module")
def contracts(request):
    from populus.utils import load_contracts
    from populus.contracts import Contract

    project_dir = getattr(request.module, "project_dir", os.getcwd())

    contracts = load_contracts(project_dir)

    contract_classes = {
        name: Contract(contract_meta, name) for name, contract_meta in contracts.items()
    }

    _dict = {
        '__iter__': lambda s: iter(contract_classes.items()),
        '__getitem__': lambda s, k: contract_classes.__getitem__[k],
    }
    _dict.update(contract_classes)

    return type('contracts', (object,), _dict)()


@pytest.fixture(scope="module")
def deployed_contracts(request, rpc_client, contracts):
    from populus.contracts import (
        deploy_contract,
        get_contract_address_from_txn,
    )
    _dict = {}

    deploy_address = getattr(request.module, 'deploy_address', rpc_client.get_coinbase())

    for contract_name, contract_class in contracts:
        txn_hash = deploy_contract(rpc_client, contract_class, _from=deploy_address)
        contract_addr = get_contract_address_from_txn(rpc_client, txn_hash)
        _dict[contract_name] = contract_class(contract_addr, rpc_client)

    return type('deployed_contracts', (object,), _dict)
