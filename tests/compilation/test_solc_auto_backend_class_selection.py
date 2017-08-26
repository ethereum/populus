import pytest

from semantic_version import (
    Spec,
)

from populus.compilation.backends import (
    SolcCombinedJSONBackend,
    SolcStandardJSONBackend,
)
from populus.compilation.backends.solc_auto import (
    get_compiler_backend_class_for_version,
)

from solc import (
    get_solc_version,
)

@pytest.mark.parametrize(
    'solc_version,backend_class',
    (
        # combined
        ('0.4.0', SolcCombinedJSONBackend),
        ('0.4.1', SolcCombinedJSONBackend),
        ('0.4.2', SolcCombinedJSONBackend),
        ('0.4.3', SolcCombinedJSONBackend),
        ('0.4.4', SolcCombinedJSONBackend),
        ('0.4.6', SolcCombinedJSONBackend),
        ('0.4.7', SolcCombinedJSONBackend),
        ('0.4.8', SolcCombinedJSONBackend),
        # standard
        ('0.4.11', SolcStandardJSONBackend),
        ('0.4.12', SolcStandardJSONBackend),
        ('0.4.13', SolcStandardJSONBackend),

    )
)
def test_get_compiler_backend_class_for_version(solc_version, backend_class, user_config):
    if backend_class is SolcCombinedJSONBackend and get_solc_version() not in Spec('<=0.4.8'):
        with pytest.raises(OSError):
            actual_backend = get_compiler_backend_class_for_version(solc_version, user_config)
    else:
        actual_backend = get_compiler_backend_class_for_version(solc_version, user_config)
        assert actual_backend.__class__ == backend_class


@pytest.mark.parametrize(
    'solc_version',
    (
        '0.4.9',
        '0.4.10',
    )
)
def test_fails_for_unsupported_solc_versions(solc_version, user_config):
    with pytest.raises(OSError):
        get_compiler_backend_class_for_version(solc_version, user_config)
