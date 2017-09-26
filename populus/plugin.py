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
    get_json_config_file_path,
)


def pytest_addoption(parser):

    parser.addoption("--populus-project", help="populus project root directory")
    parser.addini("populus_project", "populus project root directory")


def get_populus_option(cmdline_option, ini_option, environ_var, pytestconfig, default=None):

    if pytestconfig.getoption(cmdline_option, default=False):
            return pytestconfig.getoption(cmdline_option)
    else:
        if pytestconfig.getini(ini_option):
            return pytestconfig.getini(ini_option)
        elif environ_var in os.environ.keys():
            return os.environ[environ_var]

    return default


CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"


@pytest.fixture()
def project(request, pytestconfig):

    project_dir = get_populus_option(
        cmdline_option="--populus-project",
        ini_option="populus_project",
        environ_var="PYTEST_POPULUS_PROJECT",
        pytestconfig=pytestconfig,
        default=pytestconfig.args[0]
    )

    if not os.path.exists(get_json_config_file_path(project_dir)):
        raise FileNotFoundError(
            "No populus project found for testing in {project_dir}".format(
                project_dir=project_dir
            )
        )

    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)

    project = Project(project_dir, create_config_file=True)

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
