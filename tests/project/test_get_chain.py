import pytest

from populus.project import (
    Project,
)


@pytest.mark.slow
def test_project_tester_chain(project_dir):
    project = Project(project_dir)

    chain = project.get_chain('tester')

    with chain as running_tester_chain:
        web3 = running_tester_chain.web3
        assert web3.version.node.startswith('EthereumTester')
