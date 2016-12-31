import os
import pytest
from flaky import flaky
from click.testing import CliRunner

from geth.accounts import create_new_account

from web3.utils.string import force_text

from populus.project import Project

from populus.utils.filesystem import (
    get_contracts_dir,
)

from populus.cli import main


@flaky
def test_initializing_local_chain(project_dir, write_project_file):
    project = Project()

    runner = CliRunner()

    result = runner.invoke(
        main,
        ['chain', 'init', 'local_a'],
        input=((
            "0\n"              # pick deploy account.
            "Y\n"              # set account as default
        ))
    )

    assert result.exit_code == 0, result.output + str(result.exception)

    updated_project = Project()
    chain_config = updated_project.get_chain_config('local_a')
    assert 'registrar' in chain_config
    assert 'web3.eth.default_account' in chain_config
