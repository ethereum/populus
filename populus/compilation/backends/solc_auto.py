from __future__ import absolute_import

from semantic_version import (
    Spec,
    Version,
)

from solc import (
    get_solc_version,
)

from eth_utils import (
    is_string,
)

from .base import (
    BaseCompilerBackend,
)

from .solc_standard_json import (
    SolcStandardJSONBackend,
)


def get_solc_backend_class_for_version(solc_version,settings=None):

    if solc_version == "latest":
        solc_version = get_solc_version()

    elif is_string(solc_version):
        solc_version = Version(solc_version)

    if solc_version in Spec('>=0.4.11'):
        backend_class = SolcStandardJSONBackend
    else:
        raise OSError(
            "The installed solc compiler is not supported. Supported versions "
            "solc >=0.4.11"
        )

    if settings == None:
        return backend_class()
    else:
        return backend_class(settings)

