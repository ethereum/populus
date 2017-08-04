import pytest

from populus.compilation.backends import (
    SolcStandardJSONBackend,
)
from populus.compilation.backends.solc_auto import (
    get_solc_backend_class_for_version,
)


@pytest.mark.parametrize(
    'solc_version,backend_class',
    (
        # standard
        ('0.4.11', SolcStandardJSONBackend),
        ('0.4.12', SolcStandardJSONBackend),
        ('0.4.13', SolcStandardJSONBackend),
    )
)
def test_get_solc_backend_class_for_version(solc_version, backend_class):
    actual_backend_class = get_solc_backend_class_for_version(solc_version)
    assert actual_backend_class == backend_class


@pytest.mark.parametrize(
    'solc_version',
    (
        '<0.4.11',
    )
)
def test_fails_for_unsupported_solc_versions(solc_version):
    with pytest.raises(OSError):
        get_solc_backend_class_for_version(solc_version)
