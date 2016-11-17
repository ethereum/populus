from populus.utils.packaging import (
    is_local_project_package_identifier,
    construct_package_identifier,
)

from .base import (
    BasePackageBackend,
)


class LocalManifestBackend(BasePackageBackend):
    """
    Backend for package installation that can be used to install the current package.
    """
    def can_translate_package_identifier(self, package_identifier):
        return is_local_project_package_identifier(
            self.project.project_dir,
            package_identifier,
        )

    def translate_package_identifier(self, package_identifier):
        return tuple((
            construct_package_identifier(dependency_name, identifier)
            for dependency_name, identifier
            in self.project.dependencies.items()
        ))
