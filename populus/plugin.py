import pytest

from populus.project import Project

CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"


@pytest.fixture(scope="session")
def project(request):
    # This should probably be configurable using the `request` fixture but it's
    # unclear what needs to be configurable.

    project = Project()

    return project


@pytest.yield_fixture()
def chain(request, project):
    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)

    project.fill_contracts_cache(contracts, mtime)
    request.config.cache.set(CACHE_KEY_CONTRACTS, project.compiled_contract_data)
    request.config.cache.set(CACHE_KEY_MTIME, project.get_source_modification_time())

    # TODO: pull this from configuration
    with project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def web3(chain):
    return chain.web3


@pytest.fixture()
def base_contract_factories(chain):
    return chain.base_contract_factories


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts
