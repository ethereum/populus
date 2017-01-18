import pytest

from populus.migrations.migration import (
    get_migration_classes_for_execution,
)
from populus.project import Project

CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"


@pytest.fixture(scope="session")
def project(request):
    # This should probably be configurable using the `request` fixture but it's
    # unclear what needs to be configurable.

    # use pytest cache to preset the sessions project to recently compiled contracts
    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)
    project = Project()
    project.fill_contracts_cache(contracts, mtime)
    request.config.cache.set(CACHE_KEY_CONTRACTS, project.compiled_contracts)
    request.config.cache.set(CACHE_KEY_MTIME, project.get_source_modification_time())

    return project


@pytest.yield_fixture()
def unmigrated_chain(request, project):
    # TODO: pull chain name from configuration.
    with project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def chain(unmigrated_chain):
    # Determine if we have any migrations to run.
    migrations_to_execute = get_migration_classes_for_execution(
        unmigrated_chain.project.migrations,
        unmigrated_chain,
    )

    for migration in migrations_to_execute:
        migration.execute()

    return unmigrated_chain


@pytest.fixture()
def web3(unmigrated_chain):
    return unmigrated_chain.web3


@pytest.fixture()
def contract_factories(unmigrated_chain):
    return unmigrated_chain.contract_factories


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts
