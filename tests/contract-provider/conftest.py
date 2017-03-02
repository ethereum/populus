import pytest

from populus.utils.linking import (
    link_bytecode_by_name,
)


@pytest.fixture(autouse=True)
def inject_contracts(request):
    test_fn = request.function
    if not hasattr(test_fn, '_populus_contract_fixtures'):
        test_fn._populus_contract_fixtures = []
    for fixture_path in ('Math.sol', 'Library13.sol', 'Multiply13.sol'):
        if fixture_path not in test_fn._populus_contract_fixtures:
            test_fn._populus_contract_fixtures.append(fixture_path)


@pytest.fixture()
def math(chain):
    web3 = chain.web3

    Math = chain.provider.get_contract_factory('Math')

    math_address = chain.wait.for_contract_address(Math.deploy())

    return Math(address=math_address)


@pytest.fixture()
def library_13(chain):
    web3 = chain.web3

    Library13 = chain.provider.get_contract_factory('Library13')

    library_13_address = chain.wait.for_contract_address(Library13.deploy())

    return Library13(address=library_13_address)


@pytest.fixture()
def multiply_13(chain, library_13):
    web3 = chain.web3

    Multiply13 = chain.project.compiled_contract_data['Multiply13']

    bytecode = link_bytecode_by_name(
        Multiply13['bytecode'],
        Library13=library_13.address,
    )

    LinkedMultiply13 = chain.web3.eth.contract(
        abi=Multiply13['abi'],
        bytecode=bytecode,
    )

    multiply_13_address = chain.wait.for_contract_address(LinkedMultiply13.deploy())

    return LinkedMultiply13(address=multiply_13_address)
