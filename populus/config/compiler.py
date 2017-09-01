from __future__ import absolute_import

from eth_utils import (
    is_string,
)

from populus.utils.module_loading import (
    import_string,
)
from populus.config.helpers import (
    ClassImportPath,
)

from .base import Config


BACKEND_IDENTIFIER_MAP = {
    'solc:combined-json': 'populus.compilation.backends.solc.SolcCombinedJSONBackend',
    'solc:standard-json': 'populus.compilation.backends.solc.SolcStandardJSONBackend',
}


UNSUPPORTED_BACKEND_IDENTIFIER_MSG = (
    "Unsupported type. Must be either a backend class, a dot "
    "separated python path to a backend class, or one of `ipc` or "
    "`rpc`"
)


class CompilerConfig(Config):
    backend_class = ClassImportPath('class')

    def set_backend_class(self, backend_identifier):
        if isinstance(backend_identifier, type):
            self.backend_class = backend_identifier
        elif is_string(backend_identifier):
            if backend_identifier.lower() in BACKEND_IDENTIFIER_MAP:
                self.backend_class = BACKEND_IDENTIFIER_MAP[backend_identifier.lower()]
            else:
                try:
                    import_string(backend_identifier)
                except ImportError:
                    raise ValueError(
                        UNSUPPORTED_BACKEND_IDENTIFIER_MSG.format(backend_identifier)
                    )
                else:
                    self.backend_class = backend_identifier
        else:
            raise ValueError(UNSUPPORTED_BACKEND_IDENTIFIER_MSG.format(backend_identifier))

    @property
    def backend(self):
        return self.backend_class(self.backend_settings)

    @property
    def backend_settings(self):
        return self.get('settings', {})
