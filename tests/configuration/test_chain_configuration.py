import os

from populus.utils.config import (
    get_config_paths,
    load_config,
)


def test_chains_property(project_dir, write_project_file):
    ini_contents = '\n'.join((
        "[populus]",
        "project_dir={project_dir}",
        "",
        "[chain:local]",
        "provider=web3.providers.ipc.IPCProvider",
    )).format(project_dir=project_dir)
    write_project_file('populus.ini', ini_contents)

    config = load_config(get_config_paths(project_dir, []))

    assert 'local' in config.chains


def test_testing_chain_config_defaults(project_dir):
    config = load_config(get_config_paths(project_dir, []))

    assert 'testrpc' in config.chains


def test_morden_chain_config_defaults(project_dir):
    config = load_config(get_config_paths(project_dir, []))

    assert 'morden' in config.chains


def test_mainnet_chain_config_defaults(project_dir):
    config = load_config(get_config_paths(project_dir, []))

    assert 'mainnet' in config.chains


def test_custom_declared_chain_configuration(project_dir, write_project_file):
    ini_contents = '\n'.join((
        "[populus]",
        "project_dir={project_dir}",
        "",
        "[chain:mainnet]",
        "provider=web3.providers.rpc.RPCProvider",
    )).format(project_dir=project_dir)
    write_project_file('populus.ini', ini_contents)

    config = load_config(get_config_paths(project_dir, []))

    assert config.chains['mainnet']['provider'] == 'web3.providers.rpc.RPCProvider'
