import pytest

from populus.project import Project


@pytest.fixture()
def project(request):
    # TODO: allow configuring the project based on the pytest `request` object.
    return Project()


@pytest.yield_fixture()
def chain(request, project):
    # TODO: this needs to pick the chain to test against based on the project
    # config.
    chain = project.get_chain('testrpc')

    # TODO: this should run migrations.  If `testrpc` it should be snapshotted.
    # In the future we should be able to snapshot the `geth` chains too and
    # save them for faster test runs.

    with chain:
        yield chain


@pytest.fixture()
def web3(chain):
    return chain.web3


@pytest.fixture()
def contracts(chain):
    return chain.contract_factories


@pytest.fixture()
def deployed_contracts(populus_config, project, web3):
    # This should really just load from the registrar since at this point the
    # migrations have been run.
    assert False


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts
