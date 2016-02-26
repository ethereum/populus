import os
import threading

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

    # RPC Client
    ipc_path = None

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
    geth_num_accounts = 1

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


@pytest.fixture(scope="session")
def denoms():
    from ethereum.utils import denoms as _denoms
    return _denoms


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
def ipc_client(request, populus_config):
    from eth_ipc_client import Client
    ipc_path = populus_config.get_value(request, 'ipc_path')
    if ipc_path is None:
        from populus.geth import get_geth_data_dir
        geth_project_dir = populus_config.get_value(request, 'geth_project_dir')
        geth_chain_name = populus_config.get_value(request, 'geth_chain_name')
        geth_data_dir = get_geth_data_dir(geth_project_dir, geth_chain_name)
        ipc_path = os.path.join(geth_data_dir, 'geth.ipc')
    client = Client(ipc_path)
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
    elif client_type == 'ipc':
        from eth_ipc_client import Client
        ipc_path = populus_config.get_value(request, 'ipc_path')
        if ipc_path is None:
            from populus.geth import get_geth_data_dir
            geth_project_dir = populus_config.get_value(request, 'geth_project_dir')
            geth_chain_name = populus_config.get_value(request, 'geth_chain_name')
            geth_data_dir = get_geth_data_dir(geth_project_dir, geth_chain_name)
            ipc_path = os.path.join(geth_data_dir, 'geth.ipc')
        client = Client(ipc_path)
    else:
        raise ValueError(
            "Unsupported client type '{0}'.  Supported values are 'tester', "
            "'rpc', and 'ipc'"
        )

    return client


@pytest.fixture(scope="module")
def deploy_coinbase(deploy_client):
    return deploy_client.get_coinbase()


@pytest.fixture(scope="module")
def deployed_contracts(request, populus_config, deploy_client, contracts):
    from populus.deployment import deploy_contracts

    deploy_wait_for_block = int(populus_config.get_value(
        request, 'deploy_wait_for_block',
    ))
    deploy_wait_for_block_max_wait = int(populus_config.get_value(
        request, 'deploy_wait_for_block_max_wait',
    ))
    deploy_address = populus_config.get_value(
        request, 'deploy_address',
    ) or deploy_client.get_coinbase()
    deploy_max_wait = int(populus_config.get_value(
        request, 'deploy_max_wait',
    ))
    contracts_to_deploy = set(populus_config.get_value(
        request, 'deploy_contracts',
    ))
    declared_dependencies = populus_config.get_value(
        request, 'deploy_dependencies',
    )
    deploy_constructor_args = populus_config.get_value(
        request, 'deploy_constructor_args',
    )

    _deployed_contracts = deploy_contracts(
        deploy_client=deploy_client,
        contracts=contracts,
        deploy_at_block=deploy_wait_for_block,
        max_wait_for_deploy=deploy_wait_for_block_max_wait,
        from_address=deploy_address,
        max_wait=deploy_max_wait,
        contracts_to_deploy=contracts_to_deploy,
        dependencies=declared_dependencies,
        constructor_args=deploy_constructor_args,
    )

    return _deployed_contracts


@pytest.yield_fixture(scope="module")
def geth_node(request, populus_config):
    from populus.geth import (
        run_geth_node,
        get_geth_data_dir,
        get_geth_logfile_path,
        ensure_account_exists,
        create_geth_account,
        reset_chain,
        wait_for_geth_to_start,
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

    num_accounts = populus_config.get_value(request, 'geth_num_accounts')
    if num_accounts > 1:
        for _ in range(num_accounts - 1):
            create_geth_account(data_dir)

    should_reset_chain = populus_config.get_value(request, 'geth_reset_chain')

    if should_reset_chain:
        reset_chain(data_dir)

    rpc_port = populus_config.get_value(request, 'geth_rpc_port')
    rpc_host = populus_config.get_value(request, 'geth_rpc_host')

    geth_max_wait = int(populus_config.get_value(request, 'geth_max_wait'))

    command, proc = run_geth_node(data_dir, rpc_addr=rpc_host,
                                  rpc_port=rpc_port, logfile=logfile_path,
                                  verbosity="6")

    wait_for_geth_to_start(proc, max_wait=geth_max_wait)

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


@pytest.fixture(scope="module")
def geth_accounts(populus_config, request):
    from populus.geth import (
        get_geth_data_dir,
        get_geth_accounts,
    )
    geth_project_dir = populus_config.get_value(request, 'geth_project_dir')
    geth_chain_name = populus_config.get_value(request, 'geth_chain_name')
    geth_data_dir = get_geth_data_dir(geth_project_dir, geth_chain_name)

    accounts = get_geth_accounts(geth_data_dir)
    return accounts


@pytest.fixture(scope="module")
def accounts(populus_config, request):
    client_type = populus_config.get_value(request, 'deploy_client_type')
    if client_type == 'ethtester':
        from ethereum import tester
        return tuple("0x" + tester.encode_hex(account) for account in tester.accounts)
    elif client_type == 'rpc':
        raise ValueError("Not supported")
    elif client_type == 'ipc':
        raise ValueError("Not supported")
    else:
        raise ValueError("Unknown client type")
