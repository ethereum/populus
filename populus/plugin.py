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


CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"


@pytest.fixture()
def project(request):
    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)

    project = Project()

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
