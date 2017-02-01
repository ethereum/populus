import pytest


def test_base_contract_factories_fixture(project_dir, write_project_file, request,
                                         MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    base_contract_factories = request.getfuncargvalue('base_contract_factories')

    assert 'Math' in base_contract_factories


def test_deprecated_contracts_fixture(project_dir, write_project_file, request,
                                      MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    with pytest.warns(PendingDeprecationWarning):
        request.getfuncargvalue('contracts')
