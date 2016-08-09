import os
import textwrap

from populus.utils.config import (
    get_config,
)


def test_loading_single_config_file(project_dir, write_project_file):
    ini_contents = textwrap.dedent(("""
    [populus]
    project_dir={project_dir}
    """.format(project_dir=project_dir)).strip())
    write_project_file('populus.ini', ini_contents)

    config = load_config(project_dir)

    assert config['populus']['project_dir'] == project_dir


def test_loading_multiple_config_files(project_dir, write_project_file):
    primary_ini_contents = textwrap.dedent(("""
    [populus]
    project_dir={project_dir}
    """.format(project_dir=project_dir)).strip())

    write_project_file('populus.ini', primary_ini_contents)

    other_ini_contents = textwrap.dedent(("""
    [populus]
    project_dir=/should-not-override/
    """.format(project_dir=project_dir)).strip())

    write_project_file('./subdir/populus.ini', other_ini_contents)


    config = load_config(
        project_dir,
        os.path.join(project_dir, 'subdir'),
    )

    assert config['populus']['project_dir'] == project_dir
