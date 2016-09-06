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
    write_project_file('populus.ini', "[chain:local_a]")
    project = Project()

    runner = CliRunner()

    chain = project.get_chain('local_a')

    deploy_from = force_text(
        create_new_account(chain.geth.data_dir, b'a-test-password')
    )

    with chain:
        chain.wait.for_unlock(chain.web3.eth.coinbase, timeout=30)
        funding_txn_hash = chain.web3.eth.sendTransaction({
            'from': chain.web3.eth.coinbase,
            'to': deploy_from,
            'value': int(chain.web3.toWei(10, 'ether')),
        })
        chain.wait.for_receipt(funding_txn_hash, timeout=60)

    result = runner.invoke(
        main,
        ['chain', 'init'],
        input=((
            "local_a\n"          # choose chain.
            "{0}\n"              # pick deploy account.
            "Y\n"                # set account as default
            "a-test-password\n"  # unlock account
            "".format(deploy_from)
        ))
    )

    assert result.exit_code == 0, result.output + str(result.exception)

    updated_project = Project()
    assert 'registrar' in updated_project.config.chains['local_a']
    assert 'deploy_from' in updated_project.config.chains['local_a']


@flaky
def test_initializing_with_unlocked_account(project_dir, write_project_file):
    write_project_file('populus.ini', "[chain:local_a]")
    runner = CliRunner()

    result = runner.invoke(
        main,
        ['chain', 'init'],
        input=((
            "local_a\n"          # choose chain.
            "0\n"              # pick deploy account.
            "Y\n"                # set account as default
        ))
    )

    assert result.exit_code == 0, result.output + str(result.exception)

    updated_project = Project()
    assert 'registrar' in updated_project.config.chains['local_a']
    assert 'deploy_from' in updated_project.config.chains['local_a']


@flaky
def test_initializing_with_specified_chain(project_dir, write_project_file):
    write_project_file('populus.ini', "[chain:local_a]")
    runner = CliRunner()

    result = runner.invoke(
        main,
        ['chain', 'init', 'local_a'],
        input=((
            "0\n"              # pick deploy account.
            "Y\n"                # set account as default
        ))
    )

    assert result.exit_code == 0, result.output + str(result.exception)

    updated_project = Project()
    assert 'registrar' in updated_project.config.chains['local_a']
    assert 'deploy_from' in updated_project.config.chains['local_a']


@flaky
def test_initializing_no_choices(project_dir, write_project_file):
    write_project_file('populus.ini', "[chain:local_a]")
    project = Project()

    with project.get_chain('local_a') as chain:
        project.config.set('chain:local_a', 'deploy_from', chain.web3.eth.coinbase)
        project.write_config()

    runner = CliRunner()

    result = runner.invoke(
        main,
        ['chain', 'init', 'local_a'],
    )

    assert result.exit_code == 0, result.output + str(result.exception)

    updated_project = Project()
    assert 'registrar' in updated_project.config.chains['local_a']
    assert 'deploy_from' in updated_project.config.chains['local_a']
