import pytest

from populus.utils.module_loading import split_at_longest_importable_path


@pytest.mark.parametrize(
    'path,expected_import_part,expected_remainder',
    (
        ('collections.OrderedDict', 'collections', 'OrderedDict'),
        ('os.path.join', 'os.path', 'join'),
        ('itertools.chain.from_iterable', 'itertools', 'chain.from_iterable'),
    ),
)
def test_split_at_longest_importable_path(path,
                                          expected_import_part,
                                          expected_remainder):
    actual_import_part, actual_remainder = split_at_longest_importable_path(path)

    assert actual_import_part == expected_import_part
    assert actual_remainder == expected_remainder
