import pytest


from populus import Project


def test_existing_ini_file_raises_warning(project_dir, write_project_file):
    write_project_file('populus.ini')

    with pytest.warns(DeprecationWarning):
        Project()
