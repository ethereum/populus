from __future__ import absolute_import

from populus.utils.config import (
    ClassImportPath,
)

from .base import Config


class CompilationConfig(Config):
    backend_class = ClassImportPath('backend.class')

    def set_backend_class(self, backend_identifier):
        assert False

    @property
    def backend(self):
        return self.backend_class(self.backend_settings)

    @property
    def backend_settings(self):
        return self.get('backend.settings', {})
