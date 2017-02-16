import os
import itertools

from eth_utils import (
    to_tuple,
    to_dict,
    to_ordered_dict,
)

from .filesystem import (
    is_under_path,
    normpath,
)


INSTALLED_PACKAGES_BASE_DIRNAME = './installed_packages'


@normpath
def get_installed_packages_dir(base_dir):
    """
    Returns the `./installed_packages` directory for the given `base_dir`
    """
    return os.path.join(base_dir, INSTALLED_PACKAGES_BASE_DIRNAME)


@normpath
def get_dependency_base_dir(installed_packages_dir, dependency_name):
    """
    Returns the directory within `./installed_packages` that the dependency
    would be installed to.
    """
    dependency_base_dir = os.path.join(installed_packages_dir, dependency_name)
    return dependency_base_dir


def is_dependency_base_dir(directory_path):
    """
    Returns file path where the release lockfile for the current project at the
    given version.
    """
    release_lockfile_path = get_release_lockfile_path(directory_path)
    return os.path.exists(release_lockfile_path)


def extract_dependency_name_from_base_dir(dependency_base_dir):
    """
    Extract the dependency name from the directory where the dependency is
    installed
    """
    return os.path.basename(dependency_base_dir.rstrip('/'))


RELEASE_LOCKFILE_FILENAME = 'lock.json'


@normpath
def get_release_lockfile_path(dependency_base_dir):
    """
    Extract the dependency name from the directory where the dependency is
    installed
    """
    return os.path.join(dependency_base_dir, RELEASE_LOCKFILE_FILENAME)


INSTALL_IDENTIFIER_LOCKFILE_NAME = 'install_identifier.lock'


@normpath
def get_install_identifier_lockfile_path(dependency_base_dir):
    """
    Returns file path where the root identifier for the installed dependency is stored.
    """
    install_identifier_lockfile_path = os.path.join(
        dependency_base_dir,
        INSTALL_IDENTIFIER_LOCKFILE_NAME,
    )
    return install_identifier_lockfile_path


def get_install_identifier(dependency_base_dir):
    """
    Gets the install_identifier from the translated identifier lockfile
    within a dependency's base dir.
    """
    install_identifier_lockfile_path = get_install_identifier_lockfile_path(dependency_base_dir)
    with open(install_identifier_lockfile_path) as install_identifier_lockfile_file:
        install_identifier = install_identifier_lockfile_file.read().strip()
    return install_identifier


BUILD_IDENTIFIER_LOCKFILE_NAME = 'build_identifier.lock'


@normpath
def get_build_identifier_lockfile_path(dependency_base_dir):
    """
    Returns file path where the fully translated identifier for the installed
    dependency is stored.
    """
    build_identifier_lockfile_path = os.path.join(
        dependency_base_dir,
        BUILD_IDENTIFIER_LOCKFILE_NAME,
    )
    return build_identifier_lockfile_path


def get_build_identifier(dependency_base_dir):
    """
    Gets the build_identifier from the translated identifier lockfile
    within a dependency's base dir.
    """
    build_identifier_lockfile_path = get_build_identifier_lockfile_path(dependency_base_dir)
    with open(build_identifier_lockfile_path) as build_identifier_lockfile_file:
        build_identifier = build_identifier_lockfile_file.read().strip()
    return build_identifier


RELEASE_LOCKFILE_BUILD_FILENAME = '{version}.json'


@normpath
def get_lockfile_build_path(build_asset_dir, version_string):
    """
    Returns file path where the release lockfile for the current project at the
    given version.
    """
    filename = RELEASE_LOCKFILE_BUILD_FILENAME.format(version=version_string)
    release_lockfile_build_path = os.path.join(build_asset_dir, filename)
    return release_lockfile_build_path


@to_ordered_dict
def get_installed_dependency_locations(installed_packages_dir):
    if os.path.exists(installed_packages_dir):
        for maybe_package_dir in os.listdir(installed_packages_dir):
            dependency_base_dir = get_dependency_base_dir(
                installed_packages_dir,
                maybe_package_dir,
            )
            if is_dependency_base_dir(dependency_base_dir):
                yield (
                    extract_dependency_name_from_base_dir(dependency_base_dir),
                    dependency_base_dir,
                )


@to_tuple
def recursive_find_installed_dependency_base_dirs(installed_packages_dir):
    """
    Return a tuple of all filesystem paths directly under the given
    `installed_packages_dir` that look like dependency base dirs including all
    sub dependencies.
    """
    installed_dependency_locations = get_installed_dependency_locations(installed_packages_dir)

    for package_base_dir in installed_dependency_locations.values():
        yield package_base_dir

        package_installed_packages_dir = get_installed_packages_dir(package_base_dir)

        sub_base_dirs = recursive_find_installed_dependency_base_dirs(
            package_installed_packages_dir,
        )
        for sub_package_base_dir in sub_base_dirs:
            yield sub_package_base_dir


@to_dict
def build_dependency_namespace_lookups(dependency_base_dirs):
    for base_dir in dependency_base_dirs:
        dependency_name = extract_dependency_name_from_base_dir(base_dir)
        parent_dependency_names = tuple(sorted(
            extract_dependency_name_from_base_dir(parent_base_dir)
            for parent_base_dir
            in dependency_base_dirs
            if is_under_path(parent_base_dir, base_dir)
        ))
        dependency_namespace = ':'.join(itertools.chain(
            parent_dependency_names,
            (dependency_name,),
        ))
        yield (base_dir, dependency_namespace)


@to_dict
def extract_build_dependendencies_from_installed_packages(installed_packages_dir):
    """
    Extract the current installed dependencies for creation of the
    `build_dependencies` section of a release lockfile.
    """
    installed_dependency_locations = get_installed_dependency_locations(installed_packages_dir)
    for dependency_name, dependency_base_dir in installed_dependency_locations.items():
        dependency_name = extract_dependency_name_from_base_dir(dependency_base_dir)
        dependency_identifier = get_build_identifier(dependency_base_dir)
        yield dependency_name, dependency_identifier
