from populus.packages.backends.base import (
    BasePackageBackend,
)
from populus.utils.packaging import (
    compute_recursive_package_dependencies,
)


def make_manifest_and_lockfile(package_name, version='1.0.0', dependencies=None):
    manifest = {
        'package_name': package_name,
        'version': version,
    }
    if dependencies is not None:
        manifest['dependencies'] = dependencies

    lock_file = {
        'version': version,
        'package_manifest': manifest,
    }
    if dependencies is not None:
        lock_file['build_dependencies'] = dependencies
    return manifest, lock_file


OWNED_MANIFEST, OWNED_LOCKFILE = make_manifest_and_lockfile('owned', '1.0.0')
MULTIPLY_3_MANIFEST, MULTIPLY_3_LOCK_FILE = make_manifest_and_lockfile(
    'multiply-3',
    '1.0.0',
    dependencies={'owned': '1.0.0'},
)
MULTIPLY_7_MANIFEST, MULTIPLY_7_LOCK_FILE = make_manifest_and_lockfile(
    'multiply-7',
    '1.0.0',
    dependencies={'owned': '1.0.0'},
)
MULTIPLY_21_MANIFEST, MULTIPLY_21_LOCK_FILE = make_manifest_and_lockfile(
    'multiply-21',
    '1.0.0',
    dependencies={
        'multiply-3': '1.0.0',
        'multiply-7': '1.0.0',
    }
)
MATH_LIB_MANIFEST, MATH_LIB_LOCK_FILE = make_manifest_and_lockfile(
    'math-lib',
    '1.0.0',
    dependencies={
        'multiply-21': '1.0.0',
    }
)


class DummyPackageBackend(BasePackageBackend):
    known_packages = {
        'owned==1.0.0': (OWNED_MANIFEST, OWNED_LOCKFILE),
        'multiply-3==1.0.0': (MULTIPLY_3_MANIFEST, MULTIPLY_3_LOCK_FILE),
        'multiply-7==1.0.0': (MULTIPLY_7_MANIFEST, MULTIPLY_7_LOCK_FILE),
        'multiply-27==1.0.0': (MULTIPLY_21_MANIFEST, MULTIPLY_21_LOCK_FILE),
        'math-lib==1.0.0': (MATH_LIB_MANIFEST, MATH_LIB_LOCK_FILE),
    }

    def can_resolve_identifier(self, package_identifier):
        return package_identifier in self.known_packages

    def resolve_package_identifier(self, package_identifier):
        return self.known_packages[package_identifier]


def test_compute_recursive_package_dependencies():
    backends = {'dummy': DummyPackageBackend(None)}
    full_dependencies = compute_recursive_package_dependencies('multiply-7==1.0.0', backends)

    # TODO: what is the right assertion here?
    assert full_dependencies
