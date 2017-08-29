from __future__ import absolute_import
import warnings

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

from .solc_combined_json import (
    SolcCombinedJSONBackend,
)

from .solc_standard_json import (
    SolcStandardJSONBackend,
)


def get_compiler_backend_class_for_version(compiler_version, user_config):

    if compiler_version == "auto":
        compiler_version = get_solc_version()

    elif is_string(compiler_version):
        compiler_version = Version(compiler_version)

    if compiler_version in Spec('>=0.4.11'):
        backend_class = SolcStandardJSONBackend
        settings = user_config.get('compilation.backends.SolcStandardJSON.settings')
    else:
        warnings.warn(
            "Support for solc <0.4.11 will be dropped in the next populus release",
            DeprecationWarning
        )
        if compiler_version == Version('0.4.9') or compiler_version == Version('0.4.10'):
            raise OSError(
                "Version {compiler_version} is not supported".format(compiler_version=compiler_version)
            )
        backend_class = SolcCombinedJSONBackend
        settings = user_config.get('compilation.backends.SolcCombinedJSON.settings')

    return backend_class(settings)
