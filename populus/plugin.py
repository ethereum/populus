import pytest

from populus.migrations.migration import (
    get_migration_classes_for_execution,
)
from populus.project import Project

POPULUS_PROJECT_HASH = "populus/project_code_hash"
POPULUS_PROJECT_CODE = "populus/project_code"


@pytest.fixture(scope="session")
def project(request):
    # This should probably be configurable using the `request` fixture but it's
    # unclear what needs to be configurable.
    code = request.config.cache.get(POPULUS_PROJECT_CODE, None)
    code_hash = request.config.cache.get(POPULUS_PROJECT_HASH, None)
    project = Project()
    if code is not None and code_hash is not None:
        project._cached_compiled_contracts_hash = code_hash
        project._cached_compiled_contracts = code
    request.config.cache.set(POPULUS_PROJECT_CODE, project.compiled_contracts)
    request.config.cache.set(POPULUS_PROJECT_HASH, project._cached_compiled_contracts_hash)

    return project


@pytest.yield_fixture()
def unmigrated_chain(request, project):
    # This should probably allow you to specify the test chain to be used based
    # on the `request` object.  It's unclear what the best way to do this is
    # so... punt!
    chain = project.get_chain('testrpc')

    # TODO: this should run migrations.  If `testrpc` it should be snapshotted.
    # In the future we should be able to snapshot the `geth` chains too and
    # save them for faster test runs.

    with chain:
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
def contracts(unmigrated_chain):
    return unmigrated_chain.contract_factories


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts
