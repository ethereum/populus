import os

import pkg_resources


BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')


__version__ = pkg_resources.get_distribution("populus").version


from .project import Project  # NOQA


__all__ = [
    "Project",
    "ASSETS_DIR",
]
