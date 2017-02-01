from populus.migrations import (
    Migration,
    DeployContract,
)
from populus.migrations.writer import (
    write_migration,
)
from populus.migrations.migration import (
    get_migration_classes_for_execution,
)


def test_chain_fixture(project_dir, write_project_file, request, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])
    write_project_file('migrations/__init__.py')

    project = request.getfuncargvalue('project')

    chain = request.getfuncargvalue('chain')
    assert chain.web3.isConnected
