import os

from populus.utils.config import (
    get_config_paths,
    load_config,
)


def test_loading_single_config_file(project_dir, write_project_file):
    ini_contents = '\n'.join((
        "[populus]",
        "project_dir={project_dir}",
    )).format(project_dir=project_dir)
    write_project_file('populus.ini', ini_contents)

    config = load_config(get_config_paths(project_dir, []))

    assert config.get('populus', 'project_dir') == project_dir


def test_loading_multiple_config_files(project_dir, write_project_file):
    primary_ini_contents = '\n'.join((
        "[populus]",
        "project_dir={project_dir}",
    )).format(project_dir=project_dir)

    write_project_file('populus.ini', primary_ini_contents)

    other_ini_contents = '\n'.join((
        "[populus]",
        "project_dir=/should-not-override/",
    )).format(project_dir=project_dir)

    write_project_file('./subdir/populus.ini', other_ini_contents)


    config = load_config(get_config_paths(
        project_dir,
        [os.path.join(project_dir, 'subdir')],
    ))

    assert config.get('populus', 'project_dir') == project_dir
