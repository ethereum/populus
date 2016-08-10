import os
import textwrap

from populus.utils.config import (
    get_config_paths,
    load_config,
)


def test_default_chain_configuration(project_dir, write_project_file):
    ini_contents = textwrap.dedent(("""
    [populus]
    project_dir={project_dir}

    [chain:mainnet]
    network_id = 1
    """.format(project_dir=project_dir)).strip())
    write_project_file('populus.ini', ini_contents)

    config = load_config(get_config_paths(project_dir, []))

    assert 'mainnet' in config.chains
