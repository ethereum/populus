import os
import shutil
import pytest

from populus.project import (
    Project,
)

from populus.config import (
    load_user_config,
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

from populus.defaults import (
    USER_JSON_CONFIG_DEFAULTS,
    USER_JSON_CONFIG_FILENAME,
)

from populus.config.helpers import (
    get_user_default_json_config_file_path,
)


from populus.utils.filesystem import (
    ensure_path_exists,
)

CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"

BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')


#
# Hooks
#
def get_populus_option(request, cmdline_option, ini_option, environ_var, default):
    if request.config.getoption(cmdline_option):
        return request.config.getoption(cmdline_option)
    if request.config.getini(ini_option):
        return request.config.getini(ini_option)
    elif environ_var in os.environ:
        return os.environ[environ_var]
    else:
        return default


def pytest_addoption(parser):

    parser.addoption("--populus-user-config", help="populus global user config json file")
    parser.addini("populus_user_config", "populus global user config json file")
    parser.addoption("--populus-project", help="populus project root directory")
    parser.addini("populus_project", "populus project root directory")
    parser.addoption("--populus-context", help="populus testing context")
    parser.addini("populus_context", "populus testing context")


@pytest.fixture(scope="session")
def testing_user_config_path(request):
    return get_populus_option(
        request=request,
        cmdline_option="--populus-user-config",
        ini_option="populus_user_config",
        environ_var="POPULUS_USER_CONFIG",
        default=get_user_default_json_config_file_path(),
    )


@pytest.fixture(scope="session")
def testing_context(request):
    return get_populus_option(
        request=request,
        cmdline_option="--populus-context",
        ini_option="populus_context",
        environ_var="POPULUS_PYTEST_CONTEXT",
        default="user",
    )


@pytest.fixture(scope="session")
def testing_project_dir(request):
    return os.path.abspath(get_populus_option(
        request=request,
        cmdline_option="--populus-project",
        ini_option="populus_project",
        environ_var="POPULUS_PYTEST_PROJECT",
        default=str(request.config.invocation_dir),
    ))


@pytest.fixture()
def project(request,
            testing_project_dir,
            testing_context,
            testing_user_config_path):

    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)

    #if testing_context == "user":
    #    user_config = load_user_config(testing_user_config_path)
    #    project = Project(testing_project_dir, user_config, create_config_file=True)

    #elif testing_context == "populus":
    #    tmp_user_global_dir = os.path.join(os.getcwd(), '.populus')
    #    ensure_path_exists(tmp_user_global_dir)
    #    tmp_user_config_file_path = os.path.join(os.getcwd(), USER_JSON_CONFIG_FILENAME)

    #    shutil.copyfile(
    #        os.path.join(ASSETS_DIR, USER_JSON_CONFIG_DEFAULTS),
    #        tmp_user_config_file_path
    #    )

    #    user_config = load_user_config(tmp_user_config_file_path)
    #    project = Project(user_config=user_config, create_config_file=True)
    user_config = load_user_config(testing_user_config_path)
    project = Project(testing_project_dir, user_config, create_config_file=True)

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
