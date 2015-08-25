import os

import pytest

from populus.geth import (
    get_geth_accounts,
    get_geth_data_dir,
)


PROJECTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'projects')


@pytest.fixture
def project_test01(monkeypatch):
    project_dir = os.path.join(PROJECTS_DIR, 'test-01')
    monkeypatch.chdir(project_dir)
    return project_dir


@pytest.fixture
def project_test02(monkeypatch):
    project_dir = os.path.join(PROJECTS_DIR, 'test-02')
    monkeypatch.chdir(project_dir)
    return project_dir


@pytest.fixture
def project_test03(monkeypatch):
    project_dir = os.path.join(PROJECTS_DIR, 'test-03')
    monkeypatch.chdir(project_dir)
    return project_dir


def test_single_account(project_test01):
    chain_dir = get_geth_data_dir(project_test01, 'default')
    accounts = get_geth_accounts(data_dir=chain_dir)
    assert accounts == ('0xae71658b3ab452f7e4f03bda6f777b860b2e2ff2',)


def test_multiple_accounts(project_test02):
    chain_dir = get_geth_data_dir(project_test02, 'default')
    accounts = get_geth_accounts(data_dir=chain_dir)
    assert accounts == (
        '0xae71658b3ab452f7e4f03bda6f777b860b2e2ff2',
        '0xe8e085862a8d951dd78ec5ea784b3e22ee1ca9c6',
        '0x0da70f43a568e88168436be52ed129f4a9bbdaf5',
    )


def test_no_accounts(project_test03):
    chain_dir = get_geth_data_dir(project_test03, 'default')
    accounts = get_geth_accounts(data_dir=chain_dir)
    assert accounts == tuple()
