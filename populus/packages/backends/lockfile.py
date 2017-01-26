from populus.utils.packaging import (
    is_filesystem_release_lockfile_path,
    is_aliased_filesystem_release_lockfile_path,
    load_release_lockfile,
)

from .base import (
    BasePackageBackend,
)


class LocalFilesystemLockfileBackend(BasePackageBackend):
    """
    Backend for package installation that can be used to install the current package.
    """
    def can_translate_package_identifier(self, package_identifier):
        return is_aliased_filesystem_release_lockfile_path(package_identifier)

    def translate_package_identifier(self, package_identifier):
        if is_aliased_filesystem_release_lockfile_path(package_identifier):
            _, _, release_lockfile_path = package_identifier.partition('@')
            return (
                release_lockfile_path,
            )
        else:
            raise ValueError("Unsupported identifier: {0}".format(package_identifier))

    def can_resolve_to_release_lockfile(self, package_identifier):
        return is_filesystem_release_lockfile_path(package_identifier)

    def resolve_to_release_lockfile(self, package_identifier):
        if is_filesystem_release_lockfile_path(package_identifier):
            release_lockfile_path = package_identifier
        else:
            raise ValueError("Unsupported identifier: {0}".format(package_identifier))

        release_lockfile = load_release_lockfile(release_lockfile_path)
        return release_lockfile
