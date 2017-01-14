import pytest

from populus.contracts.backends.memory import MemoryBackend
from populate.packages.build import (
    construct_deployments_object,
    construct_deployments,
)


@pytest.fixture()
def memory_backend():
    return MemoryBackend(None)


def test_construct_deployments_object(project):
