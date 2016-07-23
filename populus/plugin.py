import os
import contextlib

import pytest

from web3 import Web3

from populus.utils.networking import (
    get_open_port,
    wait_for_http_connection,
)


class PopulusConfig(object):
    def __init__(self, request, tmpdir, **kwargs):
        self.request = request
        self.tmpdir = tmpdir

        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise AttributeError(
                    "Cannot set config value `{0}` that is not already a config "
                    "property".format(k)
                )
            setattr(self, k, v)

    def get(self, name):
        return getattr(
            self.request.module,
            name,
            os.environ.get(name.upper(), getattr(self, '_' + name)),
        )

    def __getitem__(self, name):
        return self.get(name)

    def __getattr__(self, name):
        return self.get(name)

    # RPC Config
    @property
    def _rpc_port(self):
        return get_open_port()

    _rpc_host = '127.0.0.1'

    # IPC Config
    _ipc_path = None

    # Contract source
    @property
    def _project_dir(self):
        return os.getcwd()

    # Deploy Client
    _web3_provider = 'tester'

    # Deployed Contracts
    _deploy_wait_for_block = 0
    _deploy_wait_for_block_max_wait = 70
    _deploy_address = None
    _deploy_max_wait = 70
    _deploy_contracts = set()
    _deploy_dependencies = {}
    _deploy_constructor_args = {}
    _deploy_gas_limit = None

    # Geth
    @property
    def _geth_base_dir(self):
        return str(self.tmpdir.mkdir("project-dir"))

    _geth_chain_name = 'default-test'
    _geth_reset_chain = True
    _geth_num_accounts = 1

    _geth_max_wait = 5


@pytest.fixture()
def populus_config(request, tmpdir):
    return PopulusConfig(request=request, tmpdir=tmpdir)


@contextlib.contextmanager
def setup_tester_rpc_provider():
    from testrpc import testrpc
    from web3.providers.rpc import TestRPCProvider

    port = get_open_port()
    provider = TestRPCProvider(port=port)

    testrpc.full_reset()
    testrpc.rpc_configure('eth_mining', False)
    testrpc.rpc_configure('eth_protocolVersion', '0x3f')
    testrpc.rpc_configure('net_version', 1)
    testrpc.evm_mine()

    wait_for_http_connection('127.0.0.1', port)
    yield provider
    provider.server.shutdown()
    provider.server.server_close()


@contextlib.contextmanager
def setup_rpc_provider():
    from web3.providers.rpc import RPCProvider

    with tempdir() as base_dir:
        geth = GethProcess('testing', base_dir=base_dir)
        geth.start()
        wait_for_http_connection(geth.rpc_port)
        provider = RPCProvider(port=geth.rpc_port)
        provider._geth = geth
        yield provider
        geth.stop()


@contextlib.contextmanager
def setup_ipc_provider():
    from web3.providers.ipc import IPCProvider

    with tempdir() as base_dir:
        geth = GethProcess('testing', base_dir=base_dir)
        geth.start()
        wait_for_ipc_connection(geth.ipc_path)
        provider = IPCProvider(geth.ipc_path)
        provider._geth = geth
        yield provider
        geth.stop()


@pytest.yield_fixture()
def web3(populus_config):
    if populus_config.web3_provider == "tester":
        setup_fn = setup_tester_rpc_provider
    elif populus_config.web3_provider == "rpc":
        raise NotImplementedError("Not Implemented")
        setup_fn = setup_rpc_provider
    elif populus_config.web3_provider == "ipc":
        raise NotImplementedError("Not Implemented")
        setup_fn = setup_ipc_provider
    else:
        raise ValueError("Unknown param")

    with setup_fn() as provider:
        _web3 = Web3(provider)
        yield _web3


@pytest.fixture()
def contracts(request, populus_config):
    # TODO:
    assert False


@pytest.fixture()
def deployed_contracts(request, populus_config, web3, contracts):
    # TODO; fix this.
    from populus.deployment import deploy_contracts

    deploy_wait_for_block = int(populus_config['deploy_wait_for_block'])
    deploy_wait_for_block_max_wait = int(populus_config['deploy_wait_for_block_max_wait'])
    deploy_address = populus_config['deploy_address'] or web3.eth.coinbase
    deploy_max_wait = int(populus_config['deploy_max_wait'])

    contracts_to_deploy = set(populus_config['deploy_contracts'])
    declared_dependencies = populus_config['deploy_dependencies']
    deploy_constructor_args = populus_config['deploy_constructor_args']

    _deployed_contracts = deploy_contracts(
        # TODO: fix call
        web3,
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


@pytest.fixture(scope="module")
def accounts(populus_config, request):
    # TODO
    assert False
