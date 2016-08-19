import os
import textwrap
from click.testing import CliRunner

from populus.utils.config import load_config

from populus.cli import main


def test_setting_with_no_config_file_lazily_creates_file(project_dir):
    populus_ini_path = os.path.join(project_dir, 'populus.ini')

    assert not os.path.exists(populus_ini_path)

    runner = CliRunner()
    result = runner.invoke(main, ['config:set', 'default_chain:testnet'])

    assert result.exit_code == 0, result.output + str(result.exception)

    assert os.path.exists(populus_ini_path)

    config = load_config([populus_ini_path])
    assert config.get('populus', 'default_chain') == 'testnet'


def test_setting_overwritting_value(project_dir, write_project_file):
    ini_contents = '\n'.join((
        "[populus]",
        "default_chain=mainnet",
    )).format(project_dir=project_dir)
    write_project_file('populus.ini', ini_contents)

    populus_ini_path = os.path.join(project_dir, 'populus.ini')

    config = load_config([populus_ini_path])
    assert config.get('populus', 'default_chain') == 'mainnet'

    runner = CliRunner()
    result = runner.invoke(main, ['config:set', 'default_chain:testnet'])

    assert result.exit_code == 0, result.output + str(result.exception)

    config = load_config([populus_ini_path])
    assert config.get('populus', 'default_chain') == 'testnet'


def test_setting_non_default_section(project_dir, write_project_file):
    ini_contents = '\n'.join((
        "[populus]",
    )).format(project_dir=project_dir)
    write_project_file('populus.ini', ini_contents)

    populus_ini_path = os.path.join(project_dir, 'populus.ini')

    config = load_config([populus_ini_path])
    assert not config.has_section('chain:mainnet')

    runner = CliRunner()
    result = runner.invoke(main, ['config:set', '--section', 'chain:mainnet', 'provider:web3.providers.rpc.RPCProvider'])

    assert result.exit_code == 0, result.output + str(result.exception)

    config = load_config([populus_ini_path])
    assert config.has_section('chain:mainnet')
    assert config.chains['mainnet']['provider'] == 'web3.providers.rpc.RPCProvider'


def test_unsetting_value(project_dir, write_project_file):
    ini_contents = '\n'.join((
        "[populus]",
        "default_chain=mainnet",
    )).format(project_dir=project_dir)
    write_project_file('populus.ini', ini_contents)

    populus_ini_path = os.path.join(project_dir, 'populus.ini')

    config = load_config([populus_ini_path])
    assert config.has_option('populus', 'default_chain')

    runner = CliRunner()
    result = runner.invoke(main, ['config:unset', 'default_chain'])

    assert result.exit_code == 0, result.output + str(result.exception)

    config = load_config([populus_ini_path])
    assert not config.has_option('populus', 'default_chain')


def test_unsetting_value_that_is_not_present(project_dir, write_project_file):
    ini_contents = '\n'.join((
        "[populus]",
    )).format(project_dir=project_dir)
    write_project_file('populus.ini', ini_contents)

    populus_ini_path = os.path.join(project_dir, 'populus.ini')

    config = load_config([populus_ini_path])
    assert not config.has_option('populus', 'default_chain')

    runner = CliRunner()
    result = runner.invoke(main, ['config:unset', 'default_chain'])

    assert result.exit_code == 0, result.output + str(result.exception)

    config = load_config([populus_ini_path])
    assert not config.has_option('populus', 'default_chain')


def test_unsetting_entire_section(project_dir, write_project_file):
    ini_contents = '\n'.join((
        "[populus]",
        "",
        "[extra_section]",
    )).format(project_dir=project_dir)
    write_project_file('populus.ini', ini_contents)

    populus_ini_path = os.path.join(project_dir, 'populus.ini')

    config = load_config([populus_ini_path])
    assert config.has_section('extra_section')

    runner = CliRunner()
    result = runner.invoke(main, ['config:unset', '--section', 'extra_section', '--no-confirm', '*'])

    assert result.exit_code == 0, result.output + str(result.exception)

    config = load_config([populus_ini_path])
    assert not config.has_section('extra_section')
