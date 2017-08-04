from __future__ import absolute_import

from eth_utils import (
    is_string,
)

from populus.utils.module_loading import (
    import_string,
)
from populus.utils.config import (
    ClassImportPath,
)

from .base import Config

UNSUPPORTED_BACKEND_IDENTIFIER_MSG = (
    "Unsupported type. Must be either a backend class, a dot "
    "separated python path to a backend class, or one of `ipc` or "
    "`rpc`"
)


class CompilerConfig(Config):

    pass
