import os
import pytest

from populus.project import Project

from populus.utils.contracts import (
    package_contracts,
)
from populus.utils.filesystem import (
    get_latest_mtime,
)
from populus.utils.json import (
    normalize_object_for_json,
)

from populus.config.helpers import (
    check_if_project_json_file_exists,
    get_user_default_json_config_file_path,
)

from populus.api.config import (
    load_user_config,
)

from populus.contracts.registrar import (
    Registrar,
)

from populus.contracts.provider import (
    Provider,
)

from populus.contracts.helpers import (
    get_provider_backends,
    get_registrar_backends,
)

from populus.chain.helpers import (
    get_chain,
)

CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"

project_root_dir = None
user_config_path = None
chain_name = None

#
# Hooks
#


def get_populus_option(cmdline_option, ini_option, environ_var, early_config, args):

    for arg in args:
        option, _, val = arg.partition("=")
        if option == cmdline_option:
            return val
    else:
        if early_config.getini(ini_option):
            return early_config.getini(ini_option)
        else:
            return os.environ.get(environ_var)


def pytest_addoption(parser):

    parser.addoption("--populus-project", help="populus project root directory")
    parser.addini("populus_project", "populus project root directory")

    parser.addoption("--populus-user-config", help="populus user config file path")
    parser.addini("populus_user_config", "populus user config file path")

    parser.addoption("--populus-chain-name", help="the chain to run the tests with")
    parser.addini("populus_chain_name", "the chain to run the tests with")


def pytest_load_initial_conftests(early_config, parser, args):

    global project_root_dir
    project_root_dir = get_populus_option(
        cmdline_option="--populus-project",
        ini_option="populus_project",
        environ_var="POPULUS_PYTEST_PROJECT",
        early_config=early_config,
        args=args
    )

    if not project_root_dir:
        root_dir = str(parser.extra_info['rootdir'])
        if check_if_project_json_file_exists(root_dir):
            project_root_dir = root_dir
        else:
            raise FileNotFoundError(
                "No populus project found for testing in {root_dir}".format(root_dir=root_dir)
            )

    global user_config_path
    user_config_path = get_populus_option(
        cmdline_option="--populus-user-config",
        ini_option="populus_user_config",
        environ_var="POPULUS_PYTEST_USER_CONFIG",
        early_config=early_config,
        args=args)

    if not user_config_path:
        user_config_path = get_user_default_json_config_file_path()

    global chain_name
    chain_name = get_populus_option(
        cmdline_option="--populus-chain-name",
        ini_option="populus_chain_name",
        environ_var="POPULUS_PYTEST_CHAIN_NAME",
        early_config=early_config,
        args=args)

    if not chain_name:
        chain_name = 'tester'


#
# Fixtures
#

@pytest.fixture(scope="session")
def user_config(request):
    global user_config_path
    return load_user_config(user_config_path)


@pytest.fixture()
def project(request, user_config):
    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)

    project = Project(project_root_dir, user_config)

    project.fill_contracts_cache(contracts, mtime)
    request.config.cache.set(
        CACHE_KEY_CONTRACTS,
        normalize_object_for_json(project.compiled_contract_data),
    )
    request.config.cache.set(
        CACHE_KEY_MTIME,
        get_latest_mtime(project.get_all_source_file_paths()),
    )

    return project


@pytest.fixture()
def chain(project, user_config):
    global chain_name
    with get_chain(chain_name, user_config, chain_dir=project.project_root_dir) as chain:
        yield chain


@pytest.fixture()
def web3(chain):
    return chain.web3


@pytest.fixture
def registrar(chain, project, web3):
    registrar_backends = get_registrar_backends(chain.contract_backends)
    registrar = Registrar(web3, registrar_backends, base_dir=project.project_root_dir)
    return registrar


@pytest.fixture
def provider(chain, project, registrar):
    provider_backends = get_provider_backends(chain.contract_backends)
    provider = Provider(chain.web3, registrar, provider_backends, project)
    return provider


@pytest.fixture()
def base_contract_factories(provider):
    return package_contracts({
        contract_name: provider.get_base_contract_factory(contract_name)
        for contract_name in provider.get_all_contract_names()
    })


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts
