import os

import pytest

from populus.project import Project
from populus.deployment import deploy_contracts


class PopulusConfig(object):
    """
    """
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

    # What chain to test against.
    _test_chain = 'testrpc'

    # Deployed Contracts
    _deploy_max_wait = 70
    _contracts_to_deploy = set()
    _deploy_constructor_args = {}


@pytest.fixture()
def populus_config(request, tmpdir):
    return PopulusConfig(request=request, tmpdir=tmpdir)


@pytest.fixture()
def project():
    return Project()


@pytest.yield_fixture()
def chain(request, project, populus_config):
    if populus_config.test_chain == "testrpc":
        chain = project.get_chain('testrpc')
    elif populus_config.web3_provider == "temp":
        chain = project.get_chain('temp', name=request.module.__name__)
    else:
        raise ValueError("Unknown param chain configuration")

    with chain:
        yield chain


@pytest.fixture()
def web3(chain):
    return chain.web3


@pytest.fixture()
def contracts(chain):
    return chain.contract_factories


@pytest.fixture()
def deployed_contracts(populus_config, project, web3):
    deploy_max_wait = int(populus_config['deploy_max_wait'])
    contracts_to_deploy = set(populus_config['contracts_to_deploy'])
    deploy_constructor_args = populus_config['deploy_constructor_args']

    compiled_contracts = project.compiled_contracts

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
