import os
import shutil

import pytest

from populus.geth import (
    create_geth_account,
    get_geth_accounts,
    get_geth_data_dir,
)


PROJECTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'projects')


@pytest.fixture
def project_test05(monkeypatch):
    project_dir = os.path.join(PROJECTS_DIR, 'test-05')
    monkeypatch.chdir(project_dir)
    default_chain_dir = get_geth_data_dir(project_dir, 'default')
    if os.path.exists(default_chain_dir):
        shutil.rmtree(default_chain_dir)
    return project_dir


def test_create_get_account(project_test05):
    data_dir = get_geth_data_dir(project_test05, 'default')
    os.mkdir(data_dir)

    assert not get_geth_accounts(data_dir)

    account_0 = create_geth_account(data_dir)
    account_1 = create_geth_account(data_dir)

    accounts = get_geth_accounts(data_dir)
    assert (account_0, account_1) == accounts
