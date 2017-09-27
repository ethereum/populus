import os

from cytoolz.functoolz import (
    compose,
    partial,
)

from populus.utils.linking import (
    expand_placeholder,
    insert_link_value,
)


def load_contract_fixture(fixture_path_or_name, dst_path=None):
    def outer(fn):
        if not hasattr(fn, '_populus_contract_fixtures'):
            fn._populus_contract_fixtures = []
        fn._populus_contract_fixtures.append(
            (fixture_path_or_name, dst_path)
        )
        return fn
    return outer


def load_test_contract_fixture(fixture_path_or_name, dst_path=None):
    def outer(fn):
        if not hasattr(fn, '_populus_test_contract_fixtures'):
            fn._populus_test_contract_fixtures = []
        fn._populus_test_contract_fixtures.append(
            (fixture_path_or_name, dst_path)
        )
        return fn
    return outer


def update_project_config(*key_value_pairs):
    def outer(fn):
        if not hasattr(fn, '_populus_config_key_value_pairs'):
            fn._populus_config_key_value_pairs = []
        fn._populus_config_key_value_pairs.extend(key_value_pairs)
        return fn
    return outer


def user_config_version(version):
    def outer(fn):
        fn._user_config_version = version
        return fn
    return outer


DEFAULT_TESTS_DIR = "./tests/"


def get_tests_dir(project_dir):
    tests_dir = os.path.join(project_dir, DEFAULT_TESTS_DIR)
    return os.path.abspath(tests_dir)


def link_bytecode_by_name(bytecode, link_references, **link_names_and_values):
    """
    Helper function for linking bytecode with a mapping of link reference names
    to their values.

    TODO: fix this as it now needs access to the source file paths which isn't ideal
    """
    link_fn = compose(*(
        partial(
            insert_link_value,
            value=link_names_and_values[
                expand_placeholder(linkref['name'], link_names_and_values.keys())
            ],
            offset=linkref['start'],
        )
        for linkref
        in link_references
    ))
    linked_bytecode = link_fn(bytecode)
    return linked_bytecode
