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


def test_get_config():
    class SubConfig(Config):
        pass

    config = Config({'a': {'b': {'c': 1}}})

    sub_config_a = config.get_config('a')
    assert isinstance(sub_config_a, Config)
    assert not isinstance(sub_config_a, SubConfig)

    sub_config_b = config.get_config('a', config_class=SubConfig)
    assert isinstance(sub_config_b, Config)
    assert isinstance(sub_config_b, SubConfig)

    sub_config_c = sub_config_b.get_config('b')
    assert isinstance(sub_config_c, Config)
    assert not isinstance(sub_config_c, SubConfig)


def test_sub_config_does_not_mutate_parent_config():
    config = Config({'a': {'b': {'c': 1}}})

    assert 'a.b.d' not in config

    sub_config = config.get_config('a.b')
    sub_config['d'] = 2

    assert 'a.b.d' not in config
