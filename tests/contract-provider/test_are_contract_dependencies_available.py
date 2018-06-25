import pytest


def test_contract_factory_availability_with_no_dependencies(chain):
    provider = chain.provider

    is_available = provider.are_contract_dependencies_available('Math')
    assert is_available is True


def test_contract_factory_availability_with_missing_dependency(chain):
    provider = chain.provider

    is_available = provider.are_contract_dependencies_available('Multiply13')
    assert is_available is False


def test_contract_factory_availability_with_bytecode_mismatch_on_dependency(chain):
    pytest.xfail('fix populus.utils.contracts.compare_bytecode')
    provider = chain.provider
    registrar = chain.registrar

    math, _ = provider.get_or_deploy_contract('Math')

    registrar.set_contract_address('Library13', math.address)

    is_available = provider.are_contract_dependencies_available('Multiply13')
    assert is_available is False


def test_contract_factory_availability_with_dependency(chain):
    provider = chain.provider

    assert not provider.are_contract_dependencies_available('Multiply13')

    library_13, _ = provider.get_or_deploy_contract('Library13')

    is_available = provider.are_contract_dependencies_available('Multiply13')
    assert is_available is True
