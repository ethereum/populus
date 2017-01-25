import pytest

import anyconfig

from populus.config import (
    Config,
)


def test_checking_config_truthyness():
    empty_config = Config()
    assert not empty_config
    assert bool(empty_config) is False

    non_empty_config = Config({'a': 3})
    assert non_empty_config
    assert bool(non_empty_config) is True


def test_checking_config_equality():
    config = Config({'a': 1, 'b': 2})
    other_config = Config({'a': 1, 'b': 2})
    plain_dict = {'a': 1, 'b': 2}
    m9dict_value = anyconfig.to_container({'a': 1, 'b': 2})

    assert config == other_config
    assert config == plain_dict
    assert config == m9dict_value


@pytest.mark.parametrize(
    'ac_merge',
    (None, anyconfig.MS_REPLACE, anyconfig.MS_NO_REPLACE, anyconfig.MS_DICTS),
)
def test_applying_config_defaults_when_key_not_present(ac_merge):
    defaults = (
        ('a.b', {'c': 1, 'd': 2}, ac_merge),
    )
    config = Config({'x': 3}, defaults)
    assert set(config.items(flatten=True)) == {
        ('a.b.c', 1),
        ('a.b.d', 2),
        ('x', 3),
    }


@pytest.mark.parametrize(
    'ac_merge',
    (anyconfig.MS_REPLACE, anyconfig.MS_NO_REPLACE, anyconfig.MS_DICTS),
)
def test_applying_config_defaults_with_merge_and_key_present(ac_merge):
    defaults = (
        ('a.b', {'c': 1, 'd': 2}, ac_merge),
    )
    config = Config({'a': {'b': {'z': 4}}, 'x': 3}, defaults)
    expected = {
        ('a.b.c', 1),
        ('a.b.d', 2),
        ('a.b.z', 4),
        ('x', 3),
    }
    assert set(config.items(flatten=True)) == expected


def test_applying_config_defaults_with_no_merge_and_key_present():
    defaults = (
        ('a.b', {'c': 1, 'd': 2}, None),
    )
    config = Config({'a': {'b': {'z': 4}}, 'x': 3}, defaults)
    expected = {
        ('a.b.z', 4),
        ('x', 3),
    }
    assert set(config.items(flatten=True)) == expected


@pytest.mark.parametrize(
    'ac_merge',
    (anyconfig.MS_REPLACE, anyconfig.MS_NO_REPLACE, anyconfig.MS_DICTS),
)
def test_applying_config_defaults_with_merge_to_reference(ac_merge):
    defaults = (
        ('a.b', {'c': 1, 'd': 2}, ac_merge),
    )
    config = Config({'a': {'b': {'$ref': 'x.y'}}, 'x': {'y': {'z': 4}}}, defaults)
    expected = {
        ('a.b.z', 4),
        ('a.b.c', 1),
        ('a.b.d', 2),
        ('x.y.z', 4),
    }
    assert set(config.items(flatten=True)) == expected


def test_applying_config_defaults_with_no_merge_to_reference():
    defaults = (
        ('a.b', {'c': 1, 'd': 2}, None),
    )
    config = Config({'a': {'b': {'$ref': 'x.y'}}, 'x': {'y': {'z': 4}}}, defaults)
    expected = {
        ('a.b.$ref', 'x.y'),
        ('x.y.z', 4),
    }
    actual = set(config.items(flatten=True))
    assert actual == expected
