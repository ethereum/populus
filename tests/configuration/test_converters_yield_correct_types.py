import os

from populus.utils.config import (
    get_config_paths,
    load_config,
)


def test_is_external_converts_to_boolean(project_dir, write_project_file):
    ini_contents = '\n'.join((
        "[chain:parity]",
        "is_external=true",
    )).format(project_dir=project_dir)
    write_project_file('populus.ini', ini_contents)

    config = load_config(get_config_paths(project_dir, []))

    assert config.chains['parity']['is_external'] is True
