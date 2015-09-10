import os
import time
import threading

import pytest


@pytest.fixture(scope="session")
def test_coinbase():
    from ethereum import tester
    return tester.encode_hex(tester.accounts[0])


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
        get_max_gas,
    )
    from populus.utils import (
        wait_for_block,
    )

    _dict = {}

    deploy_wait_for_block = getattr(request.module, 'deploy_wait_for_block', 0)
    deploy_wait_for_block_max_wait = getattr(request.module, 'deploy_wait_for_block_max_wait', 30)

    wait_for_block(rpc_client, deploy_wait_for_block, deploy_wait_for_block_max_wait)

    deploy_address = getattr(request.module, 'deploy_address', rpc_client.get_coinbase())
    deploy_max_wait = getattr(request.module, 'deploy_max_wait', 0)
    deploy_gas_limit = getattr(request.module, 'deploy_gas_limit', get_max_gas(rpc_client))

    for contract_name, contract_class in contracts:
        txn_hash = deploy_contract(
            rpc_client,
            contract_class,
            _from=deploy_address,
            gas=deploy_gas_limit,
        )
        contract_addr = get_contract_address_from_txn(
            rpc_client,
            txn_hash,
            max_wait=deploy_max_wait,
        )
        _dict[contract_name] = contract_class(contract_addr, rpc_client)

    return type('deployed_contracts', (object,), _dict)


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
        kill_proc,
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

    geth_max_wait = getattr(request.module, 'geth_max_wait', 5)

    command, proc = run_geth_node(data_dir, rpc_addr=rpc_host, rpc_port=rpc_port)

    start = time.time()
    while time.time() < start + geth_max_wait:
        output = []
        line = proc.get_output_nowait()
        if line:
            output.append(line)

        if line is None:
            continue
        if 'Starting mining operation' in line:
            break
        elif "Still generating DAG" in line:
            print(line[line.index("Still generating DAG"):])
        elif line.startswith('Fatal:'):
            kill_proc(proc)
            raise ValueError(
                "Geth Errored while starting\nerror: {0}\n\nFull Output{1}".format(
                    line, ''.join(output),
                )
            )
    else:
        kill_proc(proc)
        raise ValueError("Geth process never started\n\n{0}".format(''.join(output)))

    yield proc
    kill_proc(proc)


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
