import pytest

import numbers

from populus.utils.config import (
    ClassImportPath,
)

from populus.config import (
    Config,
)


class ConfigForTest(Config):
    dict_class = ClassImportPath('key-a')
    other_dict_class = ClassImportPath('deep.nested.key-b')


def test_throws_keyerror_when_not_set():
    config = ConfigForTest()

    with pytest.raises(KeyError):
        config.dict_class
    with pytest.raises(KeyError):
        config.other_dict_class


def test_setting_provider_class_as_string():
    config = ConfigForTest()

    'key-a' not in config
    'deep.nested.key-b' not in config

    config.dict_class = 'numbers.Complex'
    assert config.dict_class is numbers.Complex
    config.other_dict_class = 'numbers.Real'
    assert config.other_dict_class is numbers.Real


def test_setting_provider_class_as_class():
    config = ConfigForTest()

    'key-a' not in config
    'deep.nested.key-b' not in config

    config.dict_class = numbers.Complex
    assert config.dict_class is numbers.Complex
    assert config['key-a'] == 'numbers.Complex'
    config.other_dict_class = numbers.Real
    assert config.other_dict_class is numbers.Real
    assert config['deep.nested.key-b'] == 'numbers.Real'
