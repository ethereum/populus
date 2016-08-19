import pkg_resources

from .project import Project


__version__ = pkg_resources.get_distribution("populus").version


__all__ = [
    "Project",
]
