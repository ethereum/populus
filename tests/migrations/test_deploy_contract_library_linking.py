import pytest

from populus import Project
from populus.migrations import (
    DeployContract,
    Address,
)
from populus.utils.linking import (
    link_bytecode_by_name,
)


@pytest.fixture()
def prepared_project(project_dir, write_project_file, LIBRARY_13, MULTIPLY_13):
    write_project_file('contracts/Multiply13.sol', '\n'.join((
        LIBRARY_13['source'],
        MULTIPLY_13['source'],
    )))

    project = Project()

    assert 'Library13' in project.compiled_contracts
    assert 'Multiply13' in project.compiled_contracts

    return project


@pytest.yield_fixture()
def deploy_chain(prepared_project):
    with prepared_project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def library_13(deploy_chain):
    chain = deploy_chain
    web3 = chain.web3

    Library13 = chain.contract_factories.Library13
    LIBRARY_13 = chain.project.compiled_contracts['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = chain.wait.for_contract_address(library_deploy_txn_hash, timeout=30)

    assert library_deploy_txn['input'] == LIBRARY_13['code']
    assert web3.eth.getCode(library_13_address) == LIBRARY_13['code_runtime']

    return Library13(address=library_13_address)


@pytest.fixture()
def verify_multiply_13_linked(library_13, deploy_chain):
    chain = deploy_chain
    project = chain.project
    web3 = chain.web3

    LIBRARY_13 = project.compiled_contracts['Library13']

    MULTIPLY_13 = project.compiled_contracts['Multiply13']
    Multiply13 = chain.contract_factories.Multiply13

    def do_verify(deploy_operation):
        assert '__Library13__' in MULTIPLY_13['code']
        assert '__Library13__' in MULTIPLY_13['code_runtime']

        operation_receipt = deploy_operation.execute(
            chain,
            compiled_contracts={
                'Multiply13': MULTIPLY_13,
                'Library13': LIBRARY_13,
            },
        )

        deploy_txn_hash = operation_receipt['deploy-transaction-hash']
        deploy_txn = web3.eth.getTransaction(deploy_txn_hash)
        contract_address = chain.wait.for_contract_address(deploy_txn_hash, timeout=30)

        expected_code = link_bytecode_by_name(
            MULTIPLY_13['code'],
            Library13=library_13.address,
        )
        expected_runtime = link_bytecode_by_name(
            MULTIPLY_13['code_runtime'],
            Library13=library_13.address,
        )

        assert '__Library13__' not in expected_code
        assert '__Library13__' not in expected_runtime

        assert deploy_txn['input'] == expected_code
        assert web3.eth.getCode(contract_address) == expected_runtime

        contract = Multiply13(address=contract_address)

        should_be_39 = contract.call().multiply13(3)
        assert should_be_39 == 39

    return do_verify


def test_deployment_linking_with_provided_address(library_13,
                                                  verify_multiply_13_linked):
    deploy_operation = DeployContract(
        'Multiply13',
        timeout=30,
        libraries={
            'Library13': library_13.address,
        },
    )

    verify_multiply_13_linked(deploy_operation)


def test_deployment_linking_with_provided_registrar_value(deploy_chain,
                                                          library_13,
                                                          verify_multiply_13_linked):
    chain = deploy_chain
    web3 = chain.web3
    registrar = chain.registrar

    set_library_addr_txn_hash = registrar.transact().setAddress(
        'a-custom-key',
        library_13.address,
    )
    chain.wait.for_receipt(set_library_addr_txn_hash, timeout=30)

    deploy_operation = DeployContract(
        'Multiply13',
        timeout=30,
        libraries={
            'Library13': Address.defer(key='a-custom-key'),
        },
    )

    verify_multiply_13_linked(deploy_operation)


def test_deployment_linking_with_auto_lookup_from_registrar(deploy_chain,
                                                            library_13,
                                                            verify_multiply_13_linked):
    chain = deploy_chain
    web3 = chain.web3
    registrar = chain.registrar

    set_library_addr_txn_hash = registrar.transact().setAddress(
        'contract/Library13',
        library_13.address,
    )
    chain.wait.for_receipt(set_library_addr_txn_hash, timeout=30)

    deploy_operation = DeployContract(
        'Multiply13',
        timeout=30,
    )

    verify_multiply_13_linked(deploy_operation)
