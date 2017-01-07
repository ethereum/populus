import pytest

from populus.utils.linking import (
    link_bytecode_by_name,
)
from populus.contracts.exceptions import (
    NoKnownAddress,
)
from populus import Project


@pytest.yield_fixture()
def tester_chain(project_dir, write_project_file, MATH, LIBRARY_13, MULTIPLY_13):
    write_project_file('contracts/Math.sol', MATH['source'])
    write_project_file(
        'contracts/Multiply13.sol',
        '\n'.join((LIBRARY_13['source'], MULTIPLY_13['source'])),
    )

    project = Project()

    assert 'Math' in project.compiled_contract_data
    assert 'Library13' in project.compiled_contract_data
    assert 'Multiply13' in project.compiled_contract_data

    with project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def math(tester_chain):
    chain = tester_chain
    web3 = chain.web3

    Math = chain.base_contract_factories.Math
    MATH = chain.project.compiled_contract_data['Math']

    math_deploy_txn_hash = Math.deploy()
    math_deploy_txn = web3.eth.getTransaction(math_deploy_txn_hash)
    math_address = chain.wait.for_contract_address(math_deploy_txn_hash, timeout=30)

    assert math_deploy_txn['input'] == MATH['code']
    assert web3.eth.getCode(math_address) == MATH['code_runtime']

    return Math(address=math_address)


@pytest.fixture()
def library_13(tester_chain):
    chain = tester_chain
    web3 = chain.web3

    Library13 = chain.base_contract_factories.Library13
    LIBRARY_13 = chain.project.compiled_contract_data['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = chain.wait.for_contract_address(library_deploy_txn_hash, timeout=30)

    assert library_deploy_txn['input'] == LIBRARY_13['code']
    assert web3.eth.getCode(library_13_address) == LIBRARY_13['code_runtime']

    return Library13(address=library_13_address)


@pytest.fixture()
def multiply_13(tester_chain, library_13):
    chain = tester_chain
    web3 = chain.web3

    Multiply13 = chain.base_contract_factories['Multiply13']

    code = link_bytecode_by_name(
        Multiply13.code,
        **{'Library13': library_13.address}
    )
    code_runtime = link_bytecode_by_name(
        Multiply13.code_runtime,
        **{'Library13': library_13.address}
    )

    LinkedMultiply13 = chain.web3.eth.contract(
        abi=Multiply13.abi,
        code=code,
        code_runtime=code_runtime,
        source=Multiply13.source,
    )

    multiply_13_deploy_txn_hash = LinkedMultiply13.deploy()
    multiply_13_deploy_txn = web3.eth.getTransaction(multiply_13_deploy_txn_hash)
    multiply_13_address = chain.wait.for_contract_address(multiply_13_deploy_txn_hash, timeout=30)

    assert multiply_13_deploy_txn['input'] == LinkedMultiply13.code
    assert web3.eth.getCode(multiply_13_address) == LinkedMultiply13.code_runtime

    return LinkedMultiply13(address=multiply_13_address)


<<<<<<< HEAD
@pytest.fixture()
def register_address(tester_chain):
    chain = tester_chain

    def _register_address(name, value):
        register_txn_hash = tester_chain.registrar.transact().setAddress(
            'contract/{name}'.format(name=name), value,
        )
        chain.wait.for_receipt(register_txn_hash, timeout=120)
    return _register_address


<<<<<<< HEAD:tests/chain-management/test_chain_deployed_contracts_property.py
def test_with_no_deployed_contracts(tester_chain, math, register_address):
    chain = tester_chain
=======
def test_with_no_deployed_contracts(testrpc_chain, math, register_address):
    chain = testrpc_chain
    provider = chain.contract_provider
>>>>>>> dirty:tests/contract-provider/test_deployed_contracts_property.py
=======
def test_with_no_deployed_contracts(testrpc_chain, math):
    chain = testrpc_chain
    provider = chain.store.provider
>>>>>>> Get some tests passing

    assert len(provider.deployed_contracts) == 0


<<<<<<< HEAD
<<<<<<< HEAD:tests/chain-management/test_chain_deployed_contracts_property.py
def test_with_single_deployed_contract(tester_chain, math, register_address):
    chain = tester_chain
=======
def test_with_single_deployed_contract(testrpc_chain, math, register_address):
    chain = testrpc_chain
    provider = chain.contract_provider
>>>>>>> dirty:tests/contract-provider/test_deployed_contracts_property.py
=======
def test_with_single_deployed_contract(testrpc_chain, math):
    chain = testrpc_chain
    provider = chain.store.provider
    registrar = chain.store.registrar
>>>>>>> Get some tests passing

    registrar.set_contract_address('Math', math.address)

    assert len(provider.deployed_contracts) == 1
    assert 'Math' in provider.deployed_contracts
    assert provider.deployed_contracts.Math.call().multiply7(3) == 21


def test_with_multiple_deployed_contracts(tester_chain,
                                          math,
                                          library_13,
<<<<<<< HEAD
                                          multiply_13,
                                          register_address):
<<<<<<< HEAD:tests/chain-management/test_chain_deployed_contracts_property.py
    chain = tester_chain
=======
    chain = testrpc_chain
    provider = chain.contract_provider
>>>>>>> dirty:tests/contract-provider/test_deployed_contracts_property.py
=======
                                          multiply_13):
    chain = testrpc_chain
    provider = chain.store.provider
    registrar = chain.store.registrar
>>>>>>> Get some tests passing

    registrar.set_contract_address('Math', math.address)
    registrar.set_contract_address('Library13', library_13.address)
    registrar.set_contract_address('Multiply13', multiply_13.address)

    assert len(provider.deployed_contracts) == 3

    assert 'Math' in provider.deployed_contracts
    assert provider.deployed_contracts.Math.call().multiply7(3) == 21

    assert 'Library13' in provider.deployed_contracts
    assert provider.deployed_contracts.Library13.call().multiply13(3) == 39

    assert 'Multiply13' in provider.deployed_contracts
    assert provider.deployed_contracts.Multiply13.call().multiply13(3) == 39


<<<<<<< HEAD:tests/chain-management/test_chain_deployed_contracts_property.py
def test_missing_dependencies_ignored(tester_chain,
                                      math,
                                      library_13,
                                      multiply_13,
                                      register_address):
    chain = tester_chain
=======
def test_contracts_with_missing_dependencies_ignored(testrpc_chain,
                                                     math,
                                                     library_13,
                                                     multiply_13):
    chain = testrpc_chain
<<<<<<< HEAD
    provider = chain.contract_provider
>>>>>>> dirty:tests/contract-provider/test_deployed_contracts_property.py
=======
    provider = chain.store.provider
    registrar = chain.store.registrar
>>>>>>> Get some tests passing

    registrar.set_contract_address('Math', math.address)
    registrar.set_contract_address('Multiply13', multiply_13.address)

    assert len(provider.deployed_contracts) == 1

    assert 'Math' in provider.deployed_contracts
    assert provider.deployed_contracts.Math.call().multiply7(3) == 21

    assert 'Library13' not in provider.deployed_contracts
    assert 'Multiply13' not in provider.deployed_contracts
