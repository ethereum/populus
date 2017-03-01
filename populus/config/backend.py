from __future__ import absolute_import

from populus.utils.module_loading import (
    import_string,
)
from populus.utils.types import (
    is_string,
)
from populus.utils.config import (
    ClassImportPath,
)

from .base import Config


UNSUPPORTED_BACKEND_IDENTIFIER_MSG = (
    "Unsupported type. Must be either a backend class, a dot "
    "separated python path to a backend class, or one of {0}"
)


class BaseBackendConfig(Config):
    backend_class = ClassImportPath('class')
    backend_class_shortnames = None

    def set_backend_class(self, backend_identifier):
        if isinstance(backend_identifier, type):
            self.backend_class = backend_identifier
        elif is_string(backend_identifier):
            if backend_identifier.lower() in self.backend_class_shortnames:
                self.backend_class = self.backend_class_shortnames[backend_identifier.lower()]
            else:
                try:
                    import_string(backend_identifier)
                except ImportError:
                    raise ValueError(
                        UNSUPPORTED_BACKEND_IDENTIFIER_MSG.format(
                            ','.join(tuple(self.backend_class_shortnames.keys()))
                        )
                    )
                else:
                    self.backend_class = backend_identifier
        else:
            raise ValueError(
                UNSUPPORTED_BACKEND_IDENTIFIER_MSG.format(
                    ','.join(tuple(self.backend_class_shortnames.keys()))
                )
            )

    @property
    def backend(self):
        return self.backend_class(**self.backend_kwargs)

    @property
    def backend_kwargs(self):
        return self.get('settings', {})

    @backend_kwargs.setter
    def backend_kwargs(self, value):
        self['backend.settings'] = value

    @property
    def priority(self):
        return self['priority']

    @priority.setter
    def priority(self, value):
        self['priority'] = value


class ContractBackendConfig(BaseBackendConfig):
    backend_class_shortnames = {
        'memory': 'populus.contracts.backends.memory.MemoryBackend',
        'jsonfile': 'populus.contracts.backends.filesystem.JSONFileBackend',
        'project': 'populus.contracts.backends.project.ProjectContractsBackend',
    }
