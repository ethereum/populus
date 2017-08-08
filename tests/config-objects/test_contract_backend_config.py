import pytest

from populus.contracts.backends.memory import (
    MemoryBackend,
)
from populus.contracts.backends.filesystem import (
    JSONFileBackend,
)
from populus.contracts.backends.project import (
    ProjectContractsBackend,
)

from populus.config.backend import ContractBackendConfig


def test_priority_property():
    contract_backend_config = ContractBackendConfig({
        'priority': 10
    })
    assert contract_backend_config.priority == 10


def test_backend_class_property():
    contract_backend_config = ContractBackendConfig({
        'class': 'populus.contracts.backends.memory.MemoryBackend',
    })
    assert contract_backend_config.backend_class is MemoryBackend


@pytest.mark.parametrize(
    'value,expected',
    (
        ('project', 'populus.contracts.backends.project.ProjectContractsBackend'),
        ('memory', 'populus.contracts.backends.memory.MemoryBackend'),
        ('jsonfile', 'populus.contracts.backends.filesystem.JSONFileBackend'),
        ('populus.contracts.backends.project.ProjectContractsBackend', 'populus.contracts.backends.project.ProjectContractsBackend'),  # noqa: E501
        ('populus.contracts.backends.memory.MemoryBackend', 'populus.contracts.backends.memory.MemoryBackend'),  # noqa: E501
        ('populus.contracts.backends.filesystem.JSONFileBackend', 'populus.contracts.backends.filesystem.JSONFileBackend'),  # noqa: E501
        (ProjectContractsBackend, 'populus.contracts.backends.project.ProjectContractsBackend'),
        (MemoryBackend, 'populus.contracts.backends.memory.MemoryBackend'),
        (JSONFileBackend, 'populus.contracts.backends.filesystem.JSONFileBackend'),
    )
)
def test_set_backend_class_api(value, expected):
    chain_config = ContractBackendConfig()
    chain_config.set_backend_class(value)
    assert chain_config['class'] == expected
