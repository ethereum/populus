import pytest

from populus.utils.testing import load_contract_fixture


@load_contract_fixture('Math.sol')
def test_base_contract_factories_fixture(project, request):
    base_contract_factories = request.getfuncargvalue('base_contract_factories')

    assert 'Math' in base_contract_factories
