from populus.utils import (
    get_dependencies,
)


def test_single_dependencies():
    deps = {
        'Test-1': set(('Dep1', 'Dep2')),
        'Test-2': set(('Dep1',)),
    }
    assert get_dependencies('Test-1', deps) == {'Dep1', 'Dep2'}
    assert get_dependencies('Test-2', deps) == {'Dep1'}


def test_multiple_dependencies():
    deps = {
        'Test-1': set(('Dep1', 'Dep2', 'Test-3')),
        'Test-2': set(('Dep1', 'Test-1')),
        'Test-3': set(('Dep3',))
    }
    assert get_dependencies('Test-2', deps) == {'Dep1', 'Dep2', 'Dep3', 'Test-1', 'Test-3'}
