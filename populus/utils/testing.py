def load_contract_fixture(fixture_path_or_name):
    def outer(fn):
        if not hasattr(fn, '_populus_contract_fixtures'):
            fn._populus_contract_fixtures = []
        fn._populus_contract_fixtures.append(fixture_path_or_name)
        return fn
    return outer
