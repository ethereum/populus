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
from populus.utils.chains import (
    get_geth_ipc_path,
    get_data_dir as get_local_chain_datadir,
)

from populus.cli import main


@flaky
def test_initializing_local_chain(project_dir, write_project_file):
    project = Project()
    project.config['chains.local.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
    project.config['chains.local.web3.provider.settings.ipc_path'] = (
        get_geth_ipc_path(get_local_chain_datadir(project.project_dir, 'local'))
    )
    project.write_config()

    runner = CliRunner()

    result = runner.invoke(
        main,
        ['chain', 'init', 'local'],
        input=((
            "0\n"              # pick deploy account.
            "Y\n"              # set account as default
        ))
    )

    assert result.exit_code == 0, result.output + str(result.exception)

    project.reload_config()
    chain_config = updated_project.get_chain_config('local')
    assert 'registrar' in chain_config
    assert 'web3.eth.default_account' in chain_config
