import pytest


@pytest.fixture(autouse=True)
def inject_contracts(request):
    test_fn = request.function
    if not hasattr(test_fn, '_populus_contract_fixtures'):
        test_fn._populus_contract_fixtures = []
    for fixture_path in ('Math.sol', 'Library13.sol', 'Multiply13.sol'):
        if fixture_path not in test_fn._populus_contract_fixtures:
            test_fn._populus_contract_fixtures.append((fixture_path, None))
