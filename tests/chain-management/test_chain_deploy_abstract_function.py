import pytest
import textwrap
import json

import os

from populus import Project
from populus.utils.filesystem import DEFAULT_CONTRACTS_DIR
from populus.compilation import (
    compile_and_write_contracts,
)


BASE_DIR= os.path.abspath(os.path.dirname(__file__))

project_dir = os.path.join(BASE_DIR, 'projects', 'test-01')


CONTRACT_SOURCE = textwrap.dedent(("""

    contract A {

        // No body defined
        function nobody() public constant returns (bool);
    }

    contract B is A {
        uint public tested = 0x333;
    }
"""))



@pytest.yield_fixture()
def testrpc_chain(project_dir, write_project_file):
    write_project_file('contracts/Contract.sol', CONTRACT_SOURCE)

    project = Project()

    assert 'B' in project.compiled_contracts

    with project.get_chain('testrpc') as chain:
        yield chain


def test_deploy_abstract_contract(testrpc_chain):
    """We should get an exception when deploying a non-functional contract."""

    contract = testrpc_chain.get_contract("B")

    # This fails with the following
    # - Could not decode contract function call tested return data 0x for output_types ['uint256']
    assert contract.call().tested() == 0x333

