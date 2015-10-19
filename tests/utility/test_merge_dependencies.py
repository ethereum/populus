from populus.utils import (
    merge_dependencies,
)


def test_empty_dependencies():
    actual = merge_dependencies()
    assert actual == dict()


def test_single_dependencies():
    deps = {
        'Test-1': set(('Dep1', 'Dep2')),
        'Test-2': set(('Dep1',)),
    }
    actual = merge_dependencies(deps)
    assert actual == deps


def test_multiple_dependencies():
    deps_a = {
        'Test-1': set(('Dep1', 'Dep2')),
        'Test-2': set(('Dep1',)),
    }
    deps_b = {
        'Test-2': set(('Dep3',)),
        'Test-3': set(('Dep2', 'Dep3')),
    }
    deps_c = {
        'Test-1': set(('Dep3',)),
    }
    actual = merge_dependencies(deps_a, deps_b, deps_c)
    expected = {
        'Test-1': set(('Dep1', 'Dep2', 'Dep3')),
        'Test-2': set(('Dep1', 'Dep3')),
        'Test-3': set(('Dep2', 'Dep3')),
    }
    assert actual == expected
