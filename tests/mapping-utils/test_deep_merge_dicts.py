from populus.utils.mappings import (
    deep_merge_dicts,
)


def test_deep_merge_with_no_args():
    assert deep_merge_dicts() == {}


def test_deep_merge_with_single_arg():
    assert deep_merge_dicts({'a': 1, 'b': 2}) == {'a': 1, 'b': 2}


def test_deep_merge_with_multiple_args():
    expected = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    actual = deep_merge_dicts({'a': 1, 'b': 2}, {'c': 3, 'd': 4})
    assert expected == actual


def test_deep_merge_orger_precidence():
    assert deep_merge_dicts({'a': 1, 'b': 2}, {'b': 3, 'c': 4}) == {'a': 1, 'b': 3, 'c': 4}


def test_deep_merge_does_not_mutate():
    dict_a = {'a': 1, 'b': 2}
    dict_b = {'b': 3, 'c': 4}
    dict_c = {'c': 5, 'd': 6}
    assert deep_merge_dicts(dict_a, dict_b, dict_c) == {'a': 1, 'b': 3, 'c': 5, 'd': 6}
    assert dict_a == {'a': 1, 'b': 2}
    assert dict_b == {'b': 3, 'c': 4}
    assert dict_c == {'c': 5, 'd': 6}


def test_deep_merge_with_deep_dicts():
    dict_a = {'a': 1, 'b': {'x': 5, 'y': 6}}
    dict_b = {'c': 3, 'b': {'y': 7, 'z': 8}}
    dict_c = {'d': 5, 'b': {'z': 9}}
    expected = {'a': 1, 'b': {'x': 5, 'y': 7, 'z': 9}, 'c': 3, 'd': 5}
    actual = deep_merge_dicts(dict_a, dict_b, dict_c)
    assert expected == actual


def test_deep_merge_with_non_mapping_as_primary_value():
    dict_a = {'a': 1, 'b': {'x': 5, 'y': 6}}
    dict_b = {'c': 3, 'b': {'y': 7, 'z': 8}}
    dict_c = {'d': 5, 'b': 6}
    assert deep_merge_dicts(dict_a, dict_b, dict_c) == {'a': 1, 'b': 6, 'c': 3, 'd': 5}


def test_deep_merge_with_non_mappings_in_secondary_value_positions():
    dict_a = {'a': 1, 'b': {'x': 5, 'y': 6}}
    dict_b = {'c': 3, 'b': 72}
    dict_c = {'d': 5, 'b': {'z': 9}}
    expected = {'a': 1, 'b': {'x': 5, 'y': 6, 'z': 9}, 'c': 3, 'd': 5}
    actual = deep_merge_dicts(dict_a, dict_b, dict_c)
    assert expected == actual
