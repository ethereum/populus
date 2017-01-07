import pytest

from populus.project import Project

CACHE_KEY_MTIME_TEMPLATE = "populus/project/{chain_name}/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS_TEMPLATE = "populus/project/{chain_name}/compiled_contracts"


@pytest.fixture(scope="session")
def project(request):
    # This should probably be configurable using the `request` fixture but it's
    # unclear what needs to be configurable.

    project = Project()

    return project


@pytest.yield_fixture()
def chain(request, project):
    # TODO: pull this from configuration
    chain = project.get_chain('tester')

    CACHE_KEY_MTIME = CACHE_KEY_MTIME_TEMPLATE.format(chain_name=chain.chain_name)
    CACHE_KEY_CONTRACTS = CACHE_KEY_CONTRACTS_TEMPLATE.format(chain_name=chain.chain_name)

    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)

    chain.fill_contracts_cache(contracts, mtime)
    request.config.cache.set(CACHE_KEY_CONTRACTS, chain.compiled_contract_data)
    request.config.cache.set(CACHE_KEY_MTIME, chain.get_source_modification_time())

    # TODO: this should run migrations.  If `testrpc` it should be snapshotted.
    # In the future we should be able to snapshot the `geth` chains too and
    # save them for faster test runs.

    with chain:
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
