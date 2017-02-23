import os


def load_contract_fixture(fixture_path_or_name):
    def outer(fn):
        if not hasattr(fn, '_populus_contract_fixtures'):
            fn._populus_contract_fixtures = []
        fn._populus_contract_fixtures.append(fixture_path_or_name)
        return fn
    return outer


def load_test_contract_fixture(fixture_path_or_name):
    def outer(fn):
        if not hasattr(fn, '_populus_test_contract_fixtures'):
            fn._populus_test_contract_fixtures = []
        fn._populus_test_contract_fixtures.append(fixture_path_or_name)
        return fn
    return outer


def load_example_package(example_package_name):
    def outer(fn):
        if not hasattr(fn, '_populus_packages_to_load'):
            fn._populus_packages_to_load = []
        fn._populus_packages_to_load.append(example_package_name)
        return fn
    return outer


DEFAULT_TESTS_DIR = "./tests/"


def get_tests_dir(project_dir):
    tests_dir = os.path.join(project_dir, DEFAULT_TESTS_DIR)
    return os.path.abspath(tests_dir)
