import pytest
import click
from click.testing import CliRunner

from populus.project import Project
from populus.utils.cli import (
    select_chain,
)


@pytest.mark.parametrize(
    ('stdin,expected'),
    (
        ('0\n', '~~local_a~~'),
        ('1\n', '~~local_b~~'),
        ('2\n', '~~local_c~~'),
        ('3\n', '~~mainnet~~'),
        ('4\n', '~~morden~~'),
        ('5\n', '~~testrpc~~'),
        ('local_a\n', '~~local_a~~'),
        ('local_b\n', '~~local_b~~'),
        ('local_c\n', '~~local_c~~'),
        ('mainnet\n', '~~mainnet~~'),
        ('morden\n', '~~morden~~'),
        ('testrpc\n', '~~testrpc~~'),
    ),
)
def test_cli_select_chain_helper(project_dir, write_project_file, stdin, expected):
    write_project_file('populus.ini', '\n'.join((
        "[chain:local_a]",  # 0
        "",
        "[chain:local_b]",  # 1
        "",
        "[chain:local_c]",  # 2
        "",
        "[chain:mainnet]",  # 3
        "",
        "[chain:morden]",   # 4
        "",
        "[chain:testrpc]",  # 5
    )))
    project = Project()

    assert 'local_a' in project.config.chains
    assert 'local_b' in project.config.chains
    assert 'local_c' in project.config.chains

    @click.command()
    def wrapper():
        chain_name = select_chain(project)
        print("~~{0}~~".format(chain_name))

    runner = CliRunner()
    result = runner.invoke(wrapper, [], input=stdin)

    assert result.exit_code == 0
    assert expected in result.output


@pytest.mark.parametrize(
    'stdin', ('local_a\n', '20\n'),
)
def test_cli_select_chain_helper_select_invalid_options(project_dir, stdin):
    project = Project()

    assert 'local_a' not in project.config.chains
    assert len(project.config.chains) < 20

    @click.command()
    def wrapper():
        chain_name = select_chain(project)
        print("~~{0}~~".format(chain_name))

    runner = CliRunner()
    result = runner.invoke(wrapper, [], input=stdin)

    assert result.exit_code != 0
