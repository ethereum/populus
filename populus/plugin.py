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

CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"

project_root_dir = None
user_config_path = None


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

    parser.addini("populus_project", "populus project root directory")
    parser.addoption("--populus-project", help="populus project root directory")

    parser.addini("populus_user_config", "populus user config file path")
    parser.addoption("--populus-user-config", help="populus user config file path")


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


@pytest.yield_fixture()
def chain(project):
    with project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def registrar(chain):
    return chain.registrar


@pytest.fixture()
def provider(chain):
    return chain.provider


@pytest.fixture()
def web3(chain):
    return chain.web3


@pytest.fixture()
def base_contract_factories(chain):
    return package_contracts({
        contract_name: chain.provider.get_base_contract_factory(contract_name)
        for contract_name in chain.provider.get_all_contract_names()
    })


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts
