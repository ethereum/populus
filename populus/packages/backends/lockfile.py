import json

from populus.utils.packaging import (
    is_filesystem_release_lockfile_path,
    is_aliased_filesystem_release_lockfile_path,
)

from .base import (
    BasePackageBackend,
)


class LocalFilesystemLockfileBackend(BasePackageBackend):
    """
    Backend for package installation that can be used to install the current package.
    """
    def can_resolve_to_release_lockfile(self, package_identifier):
        return any((
            is_filesystem_release_lockfile_path(package_identifier),
            is_aliased_filesystem_release_lockfile_path(package_identifier),
        ))

    def resolve_to_release_lockfile(self, package_identifier):
        if is_filesystem_release_lockfile_path(package_identifier):
            release_lockfile_path = package_identifier
        elif is_aliased_filesystem_release_lockfile_path(package_identifier):
            _, _, release_lockfile_path = package_identifier.partition('@')
        else:
            raise ValueError("Unsupported identifier: {0}".format(package_identifier))

        with open(release_lockfile_path) as release_lockfile_file:
            release_lockfile = json.load(release_lockfile_file)
        return release_lockfile
