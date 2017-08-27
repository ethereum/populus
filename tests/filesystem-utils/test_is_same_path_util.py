import os

from populus.utils.filesystem import is_same_path


def test_paths_that_dont_exist():
    assert not os.path.exists('not-a-real-path')
    assert not os.path.exists('also-not-a-real-path')

    assert not is_same_path('not-a-real-path', 'also-not-a-real-path')


def test_paths_that_exist(write_project_file):
    write_project_file('not-a-real-path')
    write_project_file('also-not-a-real-path')

    assert not is_same_path('not-a-real-path', 'also-not-a-real-path')


def test_relpath_and_abspath():
    abs_path = os.path.abspath('this-is-a-path')
    rel_path = os.path.relpath('this-is-a-path')

    assert abs_path != rel_path
    assert is_same_path(abs_path, rel_path)
