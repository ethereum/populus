import pytest
import warnings

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
def _unmigrated_chain(request, project):
    # TODO: pull chain name from configuration.
    with project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def unmigrated_chain(_unmigrated_chain):
    warnings.warn(PendingDeprecationWarning(
        "The migrations API has been deprecated.  Please switch to using the "
        "`chain` fixture as the `unmigrated_chain` fixture will be removed in "
        "upcoming releases"
    ))
    return _unmigrated_chain


@pytest.fixture()
def chain(_unmigrated_chain):
    # Determine if we have any migrations to run.
    migrations_to_execute = get_migration_classes_for_execution(
        _unmigrated_chain.project.migrations,
        _unmigrated_chain,
    )

    if migrations_to_execute:
        warnings.warn(PendingDeprecationWarning(
            "The migrations API is deprecated and will be removed in the near "
            "future"
        ))

    for migration in migrations_to_execute:
        migration.execute()

    return _unmigrated_chain


@pytest.fixture()
def web3(_unmigrated_chain):
    return _unmigrated_chain.web3


@pytest.fixture()
def base_contract_factories(_unmigrated_chain):
    return _unmigrated_chain.contract_factories


@pytest.fixture()
def contracts(base_contract_factories):
    warnings.warn(PendingDeprecationWarning(
        "The `contracts` fixture has been renamed to `base_contract_factories`. "
        "The `contracts` fixture is pending deprecation and will be removed in "
        "the near future"
    ))
    return base_contract_factories


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts
