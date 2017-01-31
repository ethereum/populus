import pytest

import os

from populus.config import Config
from populus.contracts.backends.filesystem import JSONFileBackend


FILE_NAME = './registrar.json'


@pytest.fixture
def backend_config():
    return Config({
        'file_path': FILE_NAME,
    })


def test_is_provider_and_registrar_by_default(project_dir, chain, backend_config):
    backend = JSONFileBackend(chain, backend_config)
    assert backend.is_provider is True
    assert backend.is_registrar is True


def test_setting_as_only_provider(project_dir, chain, backend_config):
    backend_config['use_as_registrar'] = False
    backend = JSONFileBackend(chain, backend_config)
    assert backend.is_provider is True
    assert backend.is_registrar is False


def test_setting_as_only_registrar(project_dir, chain, backend_config):
    backend_config['use_as_provider'] = False
    backend = JSONFileBackend(chain, backend_config)
    assert backend.is_provider is False
    assert backend.is_registrar is True
