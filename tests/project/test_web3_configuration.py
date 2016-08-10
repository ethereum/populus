import textwrap
import pytest

from web3 import (
    IPCProvider,
    RPCProvider,
)
from web3.providers.rpc import (
    TestRPCProvider,
)

from populus.utils.chain import (
    get_default_ipc_path,
)
from populus.project import Project


def test_error_if_no_chain_specified_and_no_default_chain(project_dir):
    project = Project()

    with pytest.raises(AttributeError):
        project.web3


def test_uses_default_chain_when_specified(project_dir, write_project_file):
    ini_contents = textwrap.dedent(("""
    [populus]
    project_dir={project_dir}
    default_chain=custom_chain

    [chain:custom_chain]
    provider = web3.providers.ipc.IPCProvider
    """.format(project_dir=project_dir)).strip())
    write_project_file('populus.ini', ini_contents)

    project = Project()

    web3 = project.web3
    assert isinstance(web3.currentProvider, IPCProvider)


def test_default_configuration_for_test_chain(project_dir):
    project = Project(chain='test')

    web3 = project.web3
    assert isinstance(web3.currentProvider, TestRPCProvider)


def test_default_configuration_for_morden_chain(project_dir):
    project = Project(chain='morden')

    web3 = project.web3
    assert isinstance(web3.currentProvider, IPCProvider)
    assert web3.currentProvider.ipc_path == get_default_ipc_path(testnet=True)


def test_default_configuration_for_testnet_chain(project_dir):
    project = Project(chain='mainnet')

    web3 = project.web3
    assert isinstance(web3.currentProvider, IPCProvider)
    assert web3.currentProvider.ipc_path == get_default_ipc_path(testnet=False)
