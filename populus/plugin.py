import os
import time
import threading
import copy

import toposort

import pytest


class PopulusConfig(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise AttributeError(
                    "Cannot set config value `{0}` that is not already a config "
                    "property".format(k)
                )
            setattr(self, k, v)

    def get_value(self, request, name):
        """
        Utility function that tries to get the property `name` off of
        `request.module` and then falls back to looking it up in an environment
        variable, and then the specified default.
        """
        return getattr(
            request.module,
            name,
            os.environ.get(name.upper(), getattr(self, name)),
        )

    # RPC Server
    rpc_server_port = 8545
    rpc_server_host = '127.0.0.1'

    # RPC Client
    rpc_client_port = '8545'
    rpc_client_host = '127.0.0.1'

    # Contract source
    @property
    def project_dir(self):
        return os.getcwd()

    # Deploy Client
    deploy_client_type = 'ethtester'
    deploy_client_rpc_port = '8545'
    deploy_client_rpc_host = '127.0.0.1'

    # Deployed Contracts
    deploy_wait_for_block = 0
    deploy_wait_for_block_max_wait = 70
    deploy_address = None
    deploy_max_wait = 70
    deploy_contracts = set()
    deploy_dependencies = {}
    deploy_constructor_args = {}
    deploy_gas_limit = None

    # Geth
    @property
    def geth_project_dir(self):
        return os.getcwd()

    geth_chain_name = 'default-test'
    geth_reset_chain = True

    geth_rpc_port = '8545'
    geth_rpc_host = '127.0.0.1'
    geth_max_wait = 5


@pytest.fixture(scope="session")
def populus_config():
    return PopulusConfig()


@pytest.fixture(scope="session")
def ethtester_coinbase():
    from ethereum import tester
    return tester.encode_hex(tester.accounts[0])


@pytest.yield_fixture()
def testrpc_server(request, populus_config):
    from testrpc.__main__ import create_server
    from testrpc.testrpc import evm_reset

    rpc_port = populus_config.get_value(request, 'rpc_server_port')
    rpc_host = populus_config.get_value(request, 'rpc_server_host')

    server = create_server(rpc_host, rpc_port)

    evm_reset()

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    yield server

    server.shutdown()
    server.server_close()


@pytest.fixture(scope="module")
def rpc_client(request, populus_config):
    from eth_rpc_client import Client
    rpc_port = populus_config.get_value(request, 'rpc_client_port')
    rpc_hostname = populus_config.get_value(request, 'rpc_client_host')
    client = Client(rpc_hostname, rpc_port)
    return client


@pytest.fixture(scope="module")
def contracts(request, populus_config):
    from populus.utils import load_contracts
    from populus.contracts import package_contracts

    project_dir = populus_config.get_value(request, "project_dir")

    contracts = load_contracts(project_dir)
    return package_contracts(contracts)


@pytest.fixture()
def ethtester_client():
    from populus.ethtester_client import EthTesterClient
    return EthTesterClient()


@pytest.fixture(scope="module")
def deploy_client(request, populus_config):
    client_type = populus_config.get_value(request, 'deploy_client_type')

    if client_type == 'ethtester':
        from populus.ethtester_client import EthTesterClient
        client = EthTesterClient()
    elif client_type == 'rpc':
        from eth_rpc_client import Client
        rpc_host = populus_config.get_value(request, 'deploy_client_rpc_host')
        rpc_port = populus_config.get_value(request, 'deploy_client_rpc_port')
        client = Client(rpc_host, rpc_port)
    else:
        raise ValueError(
            "Unsupported client type '{0}'.  Supported values are 'tester' and "
            "'rpc'"
        )

    return client


@pytest.fixture(scope="module")
def deployed_contracts(request, populus_config, deploy_client, contracts):
    from populus.contracts import (
        deploy_contract,
        get_max_gas,
        get_linker_dependencies,
        link_contract_dependency,
    )
    from populus.utils import (
        wait_for_block,
        get_contract_address_from_txn,
        merge_dependencies,
    )

    _deployed_contracts = {}

    deploy_wait_for_block = int(populus_config.get_value(
        request, 'deploy_wait_for_block',
    ))
    deploy_wait_for_block_max_wait = int(populus_config.get_value(
        request, 'deploy_wait_for_block_max_wait',
    ))

    wait_for_block(deploy_client, deploy_wait_for_block, deploy_wait_for_block_max_wait)

    deploy_address = populus_config.get_value(
        request, 'deploy_address',
    ) or deploy_client.get_coinbase()
    deploy_max_wait = int(populus_config.get_value(
        request, 'deploy_max_wait',
    ))
    deploy_contracts = set(populus_config.get_value(
        request, 'deploy_contracts',
    ))
    declared_dependencies = populus_config.get_value(
        request, 'deploy_dependencies',
    )
    deploy_constructor_args = populus_config.get_value(
        request, 'deploy_constructor_args',
    )

    linker_dependencies = get_linker_dependencies(contracts)
    deploy_dependencies = merge_dependencies(
        declared_dependencies, linker_dependencies,
    )

    if deploy_dependencies:
        dependencies = copy.copy(deploy_dependencies)
        for contract_name, _ in contracts:
            if contract_name not in deploy_dependencies:
                dependencies[contract_name] = set()
        sorted_contract_names = toposort.toposort_flatten(dependencies)
        contracts = sorted(contracts, key=lambda c: sorted_contract_names.index(c[0]))

    for contract_name, contract_class in contracts:
        # If a subset of contracts have been specified, only deploy those.
        if deploy_contracts and contract_name not in deploy_contracts:
            continue

        constructor_args = deploy_constructor_args.get(contract_name, None)
        if callable(constructor_args):
            constructor_args = constructor_args(_deployed_contracts)

        deploy_gas_limit = int(populus_config.get_value(
            request,
            'deploy_gas_limit',
        ) or get_max_gas(deploy_client))

        if contract_name in linker_dependencies:
            for dependency_name in linker_dependencies[contract_name]:
                deployed_contract = _deployed_contracts[dependency_name]
                link_contract_dependency(contract_class, deployed_contract)

        txn_hash = deploy_contract(
            deploy_client,
            contract_class,
            constructor_args=constructor_args,
            _from=deploy_address,
            gas=deploy_gas_limit,
        )
        contract_addr = get_contract_address_from_txn(
            deploy_client,
            txn_hash,
            max_wait=deploy_max_wait,
        )
        _deployed_contracts[contract_name] = contract_class(contract_addr, deploy_client)

    return type('deployed_contracts', (object,), _deployed_contracts)


@pytest.yield_fixture(scope="module")
def geth_node(request, populus_config):
    from populus.geth import (
        run_geth_node,
        get_geth_data_dir,
        get_geth_logfile_path,
        ensure_account_exists,
        reset_chain,
    )
    from populus.utils import (
        ensure_path_exists,
        kill_proc,
    )

    project_dir = populus_config.get_value(request, 'geth_project_dir')
    chain_name = populus_config.get_value(request, 'geth_chain_name')

    data_dir = get_geth_data_dir(project_dir, chain_name)

    logfile_name_fmt = "geth-{0}-{{0}}.log".format(request.module.__name__)
    logfile_path = get_geth_logfile_path(data_dir, logfile_name_fmt)

    ensure_path_exists(data_dir)
    ensure_account_exists(data_dir)

    should_reset_chain = populus_config.get_value(request, 'geth_reset_chain')

    if should_reset_chain:
        reset_chain(data_dir)

    rpc_port = populus_config.get_value(request, 'geth_rpc_port')
    rpc_host = populus_config.get_value(request, 'geth_rpc_host')

    geth_max_wait = int(populus_config.get_value(request, 'geth_max_wait'))

    command, proc = run_geth_node(data_dir, rpc_addr=rpc_host,
                                  rpc_port=rpc_port, logfile=logfile_path,
                                  verbosity="6")

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
def geth_coinbase(request, populus_config):
    from populus.geth import (
        get_geth_data_dir,
        ensure_account_exists,
    )
    from populus.utils import (
        ensure_path_exists,
    )

    project_dir = populus_config.get_value(request, 'geth_project_dir')
    chain_name = populus_config.get_value(request, 'geth_chain_name')
    data_dir = get_geth_data_dir(project_dir, chain_name)

    ensure_path_exists(data_dir)
    geth_coinbase = ensure_account_exists(data_dir)
    return geth_coinbase
