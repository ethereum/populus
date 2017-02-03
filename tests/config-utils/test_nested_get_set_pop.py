import pytest

import copy

from populus.utils.config import (
    get_nested_key,
    set_nested_key,
    pop_nested_key,
    delete_nested_key,
)


CONFIG_DICT = {
    'a': 'z',
    'b': {'gg': 'yy'},
    'c': {'hh': 'xx', 'oo': 'pp'},
    'd': {'ii': {'jjj': 'www', 'kkk': 'vvv'}},
}


@pytest.mark.parametrize(
    'key,expected',
    (
        ('a', 'z'),
        ('b.gg', 'yy'),
        ('c.hh', 'xx'),
        ('c.oo', 'pp'),
        ('d.ii.jjj', 'www'),
        ('d.ii.kkk', 'vvv'),
    )
)
def test_get_nested_key(key, expected):
    config = copy.deepcopy(CONFIG_DICT)
    actual = get_nested_key(config, key)
    assert actual == expected


@pytest.mark.parametrize(
    'key',
    (
        'z',
        'b.z',
        'd.ii.z',
    )
)
def test_get_nested_key_with_missing_key(key):
    config = copy.deepcopy(CONFIG_DICT)
    with pytest.raises(KeyError):
        get_nested_key(config, key)


@pytest.mark.parametrize(
    'key',
    (
        # Existing paths
        'a',
        'b.gg',
        'c.hh',
        'c.oo',
        'd.ii.jjj',
        'd.ii.kkk',
        # New paths
        'z',
        'b.z',
        'd.ii.z',
    )
)
def test_set_nested_key(key):
    config = copy.deepcopy(CONFIG_DICT)
    try:
        before_value = get_nested_key(config, key)
    except KeyError:
        pass
    else:
        assert before_value != 'arst'
    set_nested_key(config, key, 'arst')
    actual = get_nested_key(config, key)
    assert actual == 'arst'


@pytest.mark.parametrize(
    'key,expected',
    (
        ('a', 'z'),
        ('b.gg', 'yy'),
        ('c.hh', 'xx'),
        ('c.oo', 'pp'),
        ('d.ii.jjj', 'www'),
        ('d.ii.kkk', 'vvv'),
    )
)
def test_pop_nested_key(key, expected):
    config = copy.deepcopy(CONFIG_DICT)
    actual = pop_nested_key(config, key)
    assert actual == expected


@pytest.mark.parametrize(
    'key,expected',
    (
        ('z', 'arst'),
        ('b.z', 'arst'),
        ('d.ii.z', 'arst'),
    )
)
def test_pop_nested_key_with_missing_key(key, expected):
    config = copy.deepcopy(CONFIG_DICT)
    with pytest.raises(KeyError):
        pop_nested_key(config, key)


@pytest.mark.parametrize(
    'key',
    (
        ('a', 'z'),
        ('b.gg', 'yy'),
        ('c.hh', 'xx'),
        ('c.oo', 'pp'),
        ('d.ii.jjj', 'www'),
        ('d.ii.kkk', 'vvv'),
    )
)
def test_delete_nested_key(key):
    config = copy.deepcopy(CONFIG_DICT)

    assert has_nested_key(config, key) is True
    delete_nested_key(config, key)
    assert has_nested_key(config, key) is False


@pytest.mark.parametrize(
    'key,expected',
    (
        ('z', 'arst'),
        ('b.z', 'arst'),
        ('d.ii.z', 'arst'),
    )
)
def test_delete_nested_key_with_missing_key(key, expected):
    config = copy.deepcopy(CONFIG_DICT)
    with pytest.raises(KeyError):
        delete_nested_key(config, key)
