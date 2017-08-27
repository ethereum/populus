import pytest


def test_contract_factory_availability_with_no_dependencies(chain, project, provider):

    is_available = provider.are_contract_dependencies_available('Math')
    assert is_available is True


def test_contract_factory_availability_with_missing_dependency(chain, project, provider):

    is_available = provider.are_contract_dependencies_available('Multiply13')
    assert is_available is False


def test_contract_factory_availability_with_bytecode_mismatch_on_dependency(chain, project, registrar, provider):

    math, _ = provider.get_or_deploy_contract('Math')

    registrar.set_contract_address('Library13', math.address)

    is_available = provider.are_contract_dependencies_available('Multiply13')
    assert is_available is False


def test_contract_factory_availability_with_dependency(chain, project, registrar, provider):

    assert not provider.are_contract_dependencies_available('Multiply13')

    library_13, _ = provider.get_or_deploy_contract('Library13')

    is_available = provider.are_contract_dependencies_available('Multiply13')
    assert is_available is True
