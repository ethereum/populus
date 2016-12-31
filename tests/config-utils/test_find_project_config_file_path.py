import pytest

import os
import itertools

from populus.utils.config import (
    find_project_config_file_path,
)
from populus.utils.filesystem import (
    is_same_path,
)


CONFIG_FILE_NAMES = (
    'populus.ini',
    'populus.yml',
    'populus.json',
)


@pytest.mark.parametrize(
    'file_name',
    CONFIG_FILE_NAMES,
)
def test_find_project_config_file_path(file_name,
                                       project_dir,
                                       write_project_file):
    write_project_file(file_name)

    expected_path = os.path.join(project_dir, file_name)

    project_config_file_path = find_project_config_file_path(project_dir)
    assert is_same_path(project_config_file_path, expected_path)


@pytest.mark.parametrize(
    'files_to_write',
    tuple(itertools.combinations(CONFIG_FILE_NAMES, 2)),
)
def test_error_when_multiple_config_files_are_present(files_to_write,
                                                      project_dir,
                                                      write_project_file):
    for file_name in files_to_write:
        write_project_file(file_name)

    with pytest.raises(ValueError):
        find_project_config_file_path(project_dir)
