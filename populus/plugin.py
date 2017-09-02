import os
import pytest

from populus.project import Project

from populus.config.helpers import (
    get_json_config_file_path,
)

from populus.utils.contracts import (
    package_contracts,
)
from populus.utils.filesystem import (
    get_latest_mtime,
)
from populus.utils.json import (
    normalize_object_for_json,
)


CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"


testing_project_dir = None
testing_context = None

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
    parser.addoption("--populus-context", help="populus testing context")
    parser.addini("populus_context", "populus testing context")


def pytest_load_initial_conftests(early_config, parser, args):

    global testing_context
    testing_context = get_populus_option(
        cmdline_option="--populus-context",
        ini_option="populus_context",
        environ_var="POPULUS_PYTEST_CONTEXT",
        early_config=early_config,
        args=args
    )

    if not testing_context:
        testing_context = 'user'

    global testing_project_dir
    testing_project_dir = get_populus_option(
        cmdline_option="--populus-project",
        ini_option="populus_project",
        environ_var="POPULUS_PYTEST_PROJECT",
        early_config=early_config,
        args=args
    )

    if testing_project_dir:
        testing_project_dir = os.path.abspath(testing_project_dir)
        if not os.path.exists(get_json_config_file_path(testing_project_dir)):
            raise FileNotFoundError(
                "No populus project found for testing in {testing_project_dir}".format(
                    testing_project_dir=testing_project_dir
                )
            )
    else:
        testing_project_dir = str(parser.extra_info['rootdir'])
        try:
            if args[0][0] != "-":
                testing_project_dir = os.path.abspath(args[0])
        except:
            pass


@pytest.fixture()
def project(request):

    global testing_project_dir
    global testing_context
    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)

    if testing_context == "user":
        project = Project(testing_project_dir, create_config_file=True)
    elif testing_context == "populus":
        project = Project(create_config_file=True)

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
