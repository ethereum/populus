import os
import threading

import pytest


class PopulusConfig(object):
    def __init__(self, request, **kwargs):
        self.request = request
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise AttributeError(
                    "Cannot set config value `{0}` that is not already a config "
                    "property".format(k)
                )
            setattr(self, k, v)

    def __getitem__(self, name):
        return getattr(
            request.module,
            name,
            os.environ.get(name.upper(), getattr(self, name)),
        )

    # RPC Config
    rpc_server_port = 8545
    rpc_server_host = '127.0.0.1'

    # IPC Config
    ipc_path = None

    # Contract source
    @property
    def project_dir(self):
        return os.getcwd()

    # Deploy Client
    web3_provider = 'ethtester'  # TODO

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


@pytest.fixture()
def populus_config(request):
    return PopulusConfig(request)


@pytest.fixture()
def web3():
    # TODO
    assert False


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
