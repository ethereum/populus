import os
import contextlib

import pytest

from web3 import Web3

from populus.deployment import deploy_contracts
from populus.utils.networking import (
    get_open_port,
    wait_for_http_connection,
)
from populus.utils.contracts import (
    package_contracts,
)
from populus.compilation import (
    compile_and_write_contracts,
)
from populus.chain import (
    testing_geth_process,
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

    # Contract source
    @property
    def _project_dir(self):
        return os.getcwd()

    # Deploy Client
    _web3_provider = 'tester'

    # Deployed Contracts
    _deploy_max_wait = 70
    _contracts_to_deploy = set()
    _deploy_constructor_args = {}


@pytest.fixture()
def populus_config(request, tmpdir):
    return PopulusConfig(request=request, tmpdir=tmpdir)


@contextlib.contextmanager
def setup_tester_rpc_provider(project_dir, test_name):
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
def setup_rpc_provider(project_dir, test_name):
    from web3.providers.rpc import RPCProvider

    with testing_geth_process(project_dir, test_name) as geth:
        provider = RPCProvider(port=geth.rpc_port)
        provider._geth = geth
        yield provider
        geth.stop()


@contextlib.contextmanager
def setup_ipc_provider(project_dir, test_name):
    from web3.providers.ipc import IPCProvider

    with testing_geth_process(project_dir, test_name) as geth:
        provider = IPCProvider(geth.ipc_path)
        provider._geth = geth
        yield provider


@pytest.yield_fixture()
def web3(request, populus_config):
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

    with setup_fn(populus_config.project_dir, request.module.__name__) as provider:
        _web3 = Web3(provider)
        yield _web3


@pytest.fixture()
def contracts(populus_config, web3):
    _, compiled_contracts, _ = compile_and_write_contracts(populus_config.project_dir)
    return package_contracts(web3, compiled_contracts)


@pytest.fixture()
def deployed_contracts(populus_config, web3):
    deploy_max_wait = int(populus_config['deploy_max_wait'])
    contracts_to_deploy = set(populus_config['contracts_to_deploy'])
    deploy_constructor_args = populus_config['deploy_constructor_args']

    _, compiled_contracts, _ = compile_and_write_contracts(populus_config.project_dir)

    _deployed_contracts = deploy_contracts(
        web3,
        all_contracts=compiled_contracts,
        contracts_to_deploy=contracts_to_deploy,
        constructor_args=deploy_constructor_args,
        timeout=deploy_max_wait,
    )

    return _deployed_contracts


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts
