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


TEST_CONFIG_DICT = {
    'a': 'z',
    'b': {'gg': 'yy'},
    'c': {'hh': 'xx', 'oo': 'pp'},
    'd': {'ii': {'jjj': 'www', 'kkk': 'vvv'}},
}

TEST_CONFIG_DEFAULTS = (
    ('b', {'gg': 'new-yy', 'hh': 'new'}, anyconfig.MS_NO_REPLACE),
    ('c', {'oo': 'new-oo', 'qq': 'new'}, anyconfig.MS_DICTS),
    ('d', {'ii': {'kkk': 'new-kkk', 'lll': 'new'}}, anyconfig.MS_REPLACE),
    ('f', {'dd': 'ee'}, anyconfig.MS_REPLACE),
    ('g', {'ddd': 'eee'}, anyconfig.MS_DICTS),
    ('h', {'dddd': 'eeee'}, anyconfig.MS_NO_REPLACE),
    ('i.jj', {'dd': 'ee'}, anyconfig.MS_REPLACE),
    ('k.ll', {'ddd': 'eee'}, anyconfig.MS_DICTS),
    ('m.nn', {'dddd': 'eeee'}, anyconfig.MS_NO_REPLACE),
)


def test_applying_config_defaults():
    config = Config(TEST_CONFIG_DICT, TEST_CONFIG_DEFAULTS)

    assert config.config_for_write == TEST_CONFIG_DICT

    # 'a':
    assert config['a'] == 'z'

    # 'b':
    assert config['b.gg'] == 'yy'
    assert config['b.hh'] == 'new'

    # 'c':
    assert config['c.hh'] == 'xx'
    assert config['c.oo'] == 'new-oo'
    assert config['c.qq'] == 'new'

    # 'd':
    assert 'd.ii.jjj' not in config
    assert config['d.ii.kkk'] == 'new-kkk'
    assert config['d.ii.lll'] == 'new'

    # 'f':
    assert config['f.dd'] == 'ee'

    # 'g':
    assert config['g.ddd'] == 'eee'

    # 'h':
    assert config['h.dddd'] == 'eeee'

    # 'i':
    assert config['i.jj.dd'] == 'ee'

    # 'h':
    assert config['k.ll.ddd'] == 'eee'

    # 'h':
    assert config['m.nn.dddd'] == 'eeee'
