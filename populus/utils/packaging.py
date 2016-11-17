import os
import hashlib
import functools
import operator
import re
import json

import semver

import jsonschema

from populus import ASSETS_DIR

from .string import (
    force_bytes,
)
from .ipfs import (
    is_ipfs_uri,
)
from .filesystem import (
    recursive_find_files,
    find_solidity_source_files,
    is_same_path,
)
from .functional import (
    cast_return_to_tuple,
    cast_return_to_dict,
    cast_return_to_ordered_dict,
)


SUPPORTED_PACKAGE_MANIFEST_VERSIONS = {'1'}


PACKAGE_MANIFEST_FILENAME = './ethpm.json'


def get_project_package_manifest_path(project_dir):
    """
    Returns filesystem path for the project's package manifest file (ethpm.json)
    """
    return os.path.join(project_dir, PACKAGE_MANIFEST_FILENAME)


INSTALLED_PACKAGES_BASE_DIRNAME = './installed_packages'


def get_installed_packages_dir(base_dir):
    """
    Returns the `./installed_packages` directory for the given `base_dir`
    """
    return os.path.join(base_dir, INSTALLED_PACKAGES_BASE_DIRNAME)


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


def get_release_lockfile_path(dependency_base_dir):
    """
    Extract the dependency name from the directory where the dependency is
    installed
    """
    return os.path.join(dependency_base_dir, RELEASE_LOCKFILE_FILENAME)


INSTALL_IDENTIFIER_LOCKFILE_NAME = 'install_identifier.lock'


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


def get_lockfile_build_path(build_asset_dir, version_string):
    """
    Returns file path where the release lockfile for the current project at the
    given version.
    """
    filename = RELEASE_LOCKFILE_BUILD_FILENAME.format(version=version_string)
    release_lockfile_build_path = os.path.join(build_asset_dir, filename)
    return release_lockfile_build_path


PACKAGE_NAME_REGEX = '[a-z][-a-z0-9]{0,213}'

EXACT_PACKAGE_NAME_REGEX = (
    "^"
    "{package_name_regex}"
    "$"
).format(
    package_name_regex=PACKAGE_NAME_REGEX,
)


def is_package_name(value):
    """
    Returns boolean whether the value is a valid package name.
    """
    return bool(re.match(EXACT_PACKAGE_NAME_REGEX, value))


def is_aliased_package_name(value):
    """
    Returns boolean whether the value is a valid package name.
    """
    alias, _, package_name = value.partition(':')
    return is_package_name(alias) and is_package_name(package_name)


IDENTIFIER_VERSION_SPECIFIERS = (
    "==",
    ">=",
    ">",
    "<=",
    "<",
)

IDENTIFIER_VERSION_COMPARISON_REGEX = "|".join(IDENTIFIER_VERSION_SPECIFIERS)

VERSION_NUMBER_PART_REGEX = "(?:0|[1-9][0-9]*)"
PRERELEASE_REGEX = (
    "(?:0|[1-9A-Za-z-][0-9A-Za-z-]*)"
    "(\.(?:0|[1-9A-Za-z-][0-9A-Za-z-]*))*"
)
BUILD_REGEX = (
    "[0-9A-Za-z-]+"
    "(\.[0-9A-Za-z-]+)*"
)

VERSON_NUMBER_REGEX = (
    "(?P<major>{version_number_part_regex})"
    "\."
    "(?P<minor>{version_number_part_regex})"
    "\."
    "(?P<patch>{version_number_part_regex})"
    "(\-(?P<prerelease>{prerelease_regex}))?"
    "(\+(?P<build>{build_regex}))?"
).format(
    version_number_part_regex=VERSION_NUMBER_PART_REGEX,
    prerelease_regex=PRERELEASE_REGEX,
    build_regex=BUILD_REGEX,
)

PACKAGE_IDENTIFIER_REGEX = (
    "(?P<package_name>{package_name_regex})"
    "((?P<version_comparison>{version_comparison_regex})(?P<version>{version_number_regex}))?"
).format(
    package_name_regex=PACKAGE_NAME_REGEX,
    version_comparison_regex=IDENTIFIER_VERSION_COMPARISON_REGEX,
    version_number_regex=VERSON_NUMBER_REGEX,
)


EXACT_PACKAGE_IDENTIFIER_REGEX = (
    "^"
    "{package_identifier_regex}"
    "$"
).format(
    package_identifier_regex=PACKAGE_IDENTIFIER_REGEX
)


def is_direct_package_identifier(value):
    """
    Returns boolean whether the value is a non-aliased package identifier which
    declares a package_name and possibly a version specifier.
    """
    return bool(re.match(EXACT_PACKAGE_IDENTIFIER_REGEX, value))


ALIASED_PACKAGE_IDENTIFIER_REGEX = (
    "^"
    "{package_name_regex}"
    "\:"
    "{package_identifier_regex}"
    "$"
).format(
    package_name_regex=PACKAGE_NAME_REGEX,
    package_identifier_regex=PACKAGE_IDENTIFIER_REGEX
)


def is_aliased_package_identifier(value):
    """
    Returns boolean whether the value is a package identifier which has an alias.
    """
    return bool(re.match(ALIASED_PACKAGE_IDENTIFIER_REGEX, value))


DEPENDENCY_VERSION_SPECIFIERS = (
    ">=",
    ">",
    "<=",
    "<",
)

DEPENDENCY_VERSION_COMPARISON_REGEX = "|".join(DEPENDENCY_VERSION_SPECIFIERS)

DEPENDENCY_VERSION_REGEX = (
    "^"
    "(?P<version_comparison>{version_comparison_regex})?(?P<version>{version_number_regex})"
    "$"
).format(
    version_comparison_regex=DEPENDENCY_VERSION_COMPARISON_REGEX,
    version_number_regex=VERSON_NUMBER_REGEX,
)


def is_version_specifier(value):
    """
    Returns boolean whether the value is a version number of version number
    range.
    """
    return bool(re.match(DEPENDENCY_VERSION_REGEX, value))


EXACT_VERSION_REGEX = (
    "^"
    "(?P<version>{version_number_regex})"
    "$"
).format(
    version_number_regex=VERSON_NUMBER_REGEX,
)


def is_exact_version(value):
    """
    Returns boolean whether the value is an exact version number
    """
    return bool(re.match(EXACT_VERSION_REGEX, value))


def is_local_project_package_identifier(project_dir, package_identifier):
    """
    Returns boolean whether the value is the filesystem path to this project
    directory.
    """
    if not os.path.exists(package_identifier):
        return False
    return is_same_path(package_identifier, project_dir)


def is_aliased_ipfs_uri(value):
    """
    Returns boolean whether the value is an IPFS URI with an alias.
    """
    dependency_name, _, maybe_ipfs_uri = value.partition('@')
    return all((
        is_package_name(dependency_name),
        is_ipfs_uri(maybe_ipfs_uri)
    ))


def is_filesystem_release_lockfile_path(package_identifier):
    """
    Returns boolean whether the value a filesystem path to a release lockfile.
    """
    if not os.path.exists(package_identifier):
        return False
    elif not os.path.isfile(package_identifier):
        return False

    try:
        load_release_lockfile(package_identifier)
    except json.JSONDecodeError:
        return False

    return True


def is_aliased_filesystem_release_lockfile_path(package_identifier):
    """
    Returns boolean whether the value a filesystem path to a release lockfile
    with an alias.
    """
    dependency_name, _, maybe_release_lockfile_path = package_identifier.partition('@')
    return all((
        is_package_name(dependency_name),
        is_filesystem_release_lockfile_path(maybe_release_lockfile_path),
    ))


def parse_package_identifier(value):
    """
    Parse a package identifier returning the package name, the type of version
    comparison and the version number for that comparison.  Both
    version_comparison and version may be `None`
    """
    if is_aliased_package_identifier(value):
        _, _, value = value.partition(':')

    match = re.match(PACKAGE_IDENTIFIER_REGEX, value)
    if match is None:
        raise ValueError("Unsupported package identifier format: {0}".format(value))
    parts = match.groupdict()
    return parts['package_name'], parts['version_comparison'], parts['version']


def construct_package_identifier(dependency_name, dependency_identifier):
    """
    Construct a package identifier string from a dependency name and the
    associated identifier.
    """
    if is_direct_package_identifier(dependency_identifier):
        return "{dependency_name}:{package_identifier}".format(
            dependency_name=dependency_name,
            package_identifier=dependency_identifier,
        )
    elif is_ipfs_uri(dependency_identifier):
        return "{dependency_name}@{ipfs_uri}".format(
            dependency_name=dependency_name,
            ipfs_uri=dependency_identifier,
        )
    elif is_version_specifier(dependency_identifier):
        if is_exact_version(dependency_identifier):
            return "{dependency_name}=={version}".format(
                dependency_name=dependency_name,
                version=dependency_identifier,
            )
        else:
            return "{dependency_name}{version}".format(
                dependency_name=dependency_name,
                version=dependency_identifier,
            )
    else:
        raise ValueError("Unsupported Identifier: '{0}'".format(dependency_identifier))


def construct_dependency_identifier(dependency_name, install_identifier, build_identifier):
    if is_direct_package_identifier(install_identifier):
        package_name, comparison, version = parse_package_identifier(install_identifier)
        if package_name == dependency_name:
            if comparison == '==':
                return version
            else:
                return ''.join((comparison, version))
        else:
            return install_identifier
    elif is_ipfs_uri(install_identifier):
        return install_identifier
    else:
        raise ValueError("Unsupported root identifier: {0}".format(install_identifier))


def extract_dependency_name_from_identifier_lineage(package_identifier_lineage,
                                                    release_lockfile):
    """
    Extracts and returns the `dependency_name` from the list of translated
    identifier names.
    """
    for package_identifier in package_identifier_lineage:
        if is_aliased_package_identifier(package_identifier):
            dependency_name, _, _ = package_identifier.partition(':')
            return dependency_name
        elif is_aliased_ipfs_uri(package_identifier):
            dependency_name, _, _ = package_identifier.partition('@')
            return dependency_name
        elif is_aliased_filesystem_release_lockfile_path(package_identifier):
            dependency_name, _, _ = package_identifier.partition('@')
            return dependency_name
        elif is_package_name(package_identifier):
            return package_identifier
        elif is_direct_package_identifier(package_identifier):
            package_name, _, _ = parse_package_identifier(package_identifier)
            return package_name
    return release_lockfile['package_name']


def validate_package_manifest(package_manifest):
    """
    Validate a package manifest against the expected schema.
    """
    # TODO: implement jsonschema validation
    pass


RELEASE_LOCKFILE_SCHEMA_FILENAME = 'release-lockfile-v1.schema.json'


def load_release_lockfile_schema():
    schema_path = os.path.join(ASSETS_DIR, RELEASE_LOCKFILE_SCHEMA_FILENAME)
    with open(schema_path) as schema_file:
        schema = json.load(schema_file)
    return schema


def validate_release_lockfile(release_lockfile):
    """
    Validate a release lockfile against the expected schema.

    TODO: additional validation that isn't covered by the JSON-schema
    - valid relative file paths
    - referenced package names
    - whatever else...
    """
    release_lockfile_schema = load_release_lockfile_schema()
    jsonschema.validate(release_lockfile, release_lockfile_schema)


def load_release_lockfile(release_lockfile_path, validate=True):
    with open(release_lockfile_path) as release_lockfile_file:
        release_lockfile = json.load(release_lockfile_file)

    if validate:
        validate_release_lockfile(release_lockfile)
    return release_lockfile


def write_release_lockfile(release_lockfile, release_lockfile_path):
    with open(release_lockfile_path, 'w') as release_lockfile_file:
        json.dump(release_lockfile, release_lockfile_file, sort_keys=True, indent=2)


def extract_install_identifier(package_identifier_lineage):
    """
    Returns the root identifier from the translated lineage of the package
    identifier.
    """
    for identifier in package_identifier_lineage:
        if is_package_name(identifier):
            continue
        elif is_direct_package_identifier(identifier):
            return identifier
        elif is_ipfs_uri(identifier):
            return identifier
    else:
        raise ValueError("No valid root identifiers found in package identifier lineage")


def extract_package_metadata(package_identifier_lineage,
                             release_lockfile):
    """
    Construct the installation metadata.
    """
    return {
        'version': release_lockfile['version'],
        'package_name': release_lockfile['package_name'],
        'dependency_name': extract_dependency_name_from_identifier_lineage(
            package_identifier_lineage,
            release_lockfile,
        ),
        'install_identifier': extract_install_identifier(package_identifier_lineage),
        'build_identifier': package_identifier_lineage[-1],
    }


def translate_package_identifier(package_identifier, package_backends):
    """
    Find the first backend which can translate the given `package_identifier`
    and return the translated package identifier.
    """
    for backend in package_backends.values():
        if backend.can_translate_package_identifier(package_identifier):
            return backend.translate_package_identifier(package_identifier)
    else:
        raise ValueError(
            "No package backends are able to translate the identifier: "
            "{0}".format(package_identifier)
        )


def fingerprint_identifier(package_identifier):
    """
    Construct a simple hash of the package identifier.  This is used to detect
    recursive circular translation loops.
    """
    return hashlib.md5(force_bytes(package_identifier)).hexdigest()


@cast_return_to_dict
def compute_identifier_tree(identifier_set, package_backends, seen_fingerprints=None):
    """
    Compute the directed acyclic graph of the package identifiers.  All leaf
    nodes are package identifiers which can be resolved to their release
    lockfiles.
    """
    if seen_fingerprints is None:
        seen_fingerprints = set()

    for package_identifier in identifier_set:
        is_resolvable = any(
            backend.can_resolve_to_release_lockfile(package_identifier)
            for backend
            in package_backends.values()
        )
        is_translatable = any(
            backend.can_translate_package_identifier(package_identifier)
            for backend
            in package_backends.values()
        )

        if is_resolvable:
            yield package_identifier, None
        elif is_translatable:
            fingerprint = fingerprint_identifier(package_identifier)
            if fingerprint in seen_fingerprints:
                raise ValueError("Translation error.  Non-acyclic tranlation graph detected")

            translated_package_identifiers = translate_package_identifier(
                package_identifier,
                package_backends,
            )

            yield (
                package_identifier,
                compute_identifier_tree(
                    translated_package_identifiers,
                    package_backends,
                    seen_fingerprints={fingerprint} | seen_fingerprints,
                ),
            )
        else:
            raise ValueError(
                "Untranslatable and Unresolvable identifier: {0}".format(package_identifier)
            )


@cast_return_to_tuple
def flatten_identifier_tree(identifier_tree):
    """
    Takes the identifier tree produced by `compute_identifier_tree`
    and flattens it so that there is one entry for each leaf node.
    """
    for key, value in identifier_tree.items():
        if value is None:
            yield (key,)
        else:
            for sub_value in flatten_identifier_tree(value):
                yield (key,) + sub_value


def resolve_to_release_lockfile(package_identifier, package_backends):
    """
    Find the first backend which can resolve the package identifier to the
    release lockfile and return the resolved release lockfile.
    """
    for _, backend in package_backends.items():
        if backend.can_resolve_to_release_lockfile(package_identifier):
            return backend.resolve_to_release_lockfile(package_identifier)
    else:
        raise ValueError(
            "None of the configured package backends support resolving the "
            "identifier '{0}'".format(package_identifier)
        )


def resolve_package_source_tree(release_lockfile, package_backends):
    """
    Find the first backend which can resolve package source tree for te geven
    release lockfile and return the resolved package source tree.
    """
    for _, backend in package_backends.items():
        if backend.can_resolve_package_source_tree(release_lockfile):
            return backend.resolve_package_source_tree(release_lockfile)
        else:
            continue
    else:
        if not release_lockfile.get('sources'):
            return {}
        raise ValueError(
            "None of the configured package backends could resolve the source tree for"
            "'{0}'".format(release_lockfile)
        )


def persist_package_file(file_path, package_backends):
    """
    Find the first backend which is capable of persisting the given file path
    and persist the given file.
    """
    for backend in package_backends.values():
        if backend.can_persist_package_file(file_path):
            return backend.persist_package_file(file_path)
    else:
        raise ValueError(
            "None of the configured package backends could persist '{0}'".format(
                file_path,
            )
        )


@cast_return_to_ordered_dict
def get_publishable_backends(release_lockfile, release_lockfile_uri, package_backends):
    """
    Return the package backends which are capable of publishing the given
    release lockfile and corresponding URI.
    """
    for backend_name, backend in package_backends.items():
        if backend.can_publish_release_lockfile(release_lockfile, release_lockfile_uri):
            yield backend_name, backend


def recursively_resolve_package_data(package_identifier_lineage, package_backends):
    """
    Given a fully translated package identifier lineage, resolve all release
    lockfiles and underlying package source trees.
    """
    release_lockfile = resolve_to_release_lockfile(
        package_identifier_lineage[-1],
        package_backends,
    )

    package_source_tree = resolve_package_source_tree(release_lockfile, package_backends)

    # Validate
    validate_release_lockfile(release_lockfile)

    # Compute package metadata
    package_meta = extract_package_metadata(
        package_identifier_lineage,
        release_lockfile,
    )

    package_build_dependencies = release_lockfile.get('build_dependencies', {})

    dependency_identifiers = tuple(
        construct_package_identifier(dependency_name, dependency_identifier)
        for dependency_name, dependency_identifier
        in package_build_dependencies.items()
    )
    dependency_identifier_tree = compute_identifier_tree(
        dependency_identifiers,
        package_backends,
    )
    flattened_dependency_identifier_tree = flatten_identifier_tree(
        dependency_identifier_tree,
    )

    resolved_dependencies = tuple(
        recursively_resolve_package_data(
            dependency_identifier_lineage,
            package_backends,
        ) for dependency_identifier_lineage in flattened_dependency_identifier_tree
    )

    return {
        'meta': package_meta,
        'lockfile': release_lockfile,
        'source_tree': package_source_tree,
        'dependencies': resolved_dependencies,
    }


def is_version_match(version, comparison, version_target):
    """
    Return boolean whether the `version` matches the `version_target` for the
    given string representation of the comparison.
    """
    if comparison == '==':
        comparison_fn = operator.eq
    elif comparison == '>':
        comparison_fn = operator.gt
    elif comparison == '>=':
        comparison_fn = operator.ge
    elif comparison == '<':
        comparison_fn = operator.lt
    elif comparison == '<=':
        comparison_fn = operator.le
    else:
        raise ValueError("Unsupported comparison")

    version_info = semver.parse_version_info(version)
    version_target_info = semver.parse_version_info(version_target)

    return comparison_fn(version_info, version_target_info)


def filter_versions(comparison, version_target, all_versions):
    """
    Return the version strings from `all_versions` which match `version_target`
    for the given comparison.
    """
    return {
        version
        for version
        in all_versions
        if is_version_match(version, comparison, version_target)
    }


def get_max_version(all_versions):
    """
    Return the largest version from the given versions.
    """
    if not all_versions:
        raise ValueError('Must pass in at least 1 version string.')
    return functools.reduce(semver.max_ver, all_versions)


EXCLUDE_INSTALLED_PACKAGES_GLOB = "./installed_packages/*"


@cast_return_to_tuple
def find_package_source_files(dependency_base_dir):
    """
    Find all of the solidity source files for the given dependency, excluding
    any of the source files that belong to any sub-dependencies.
    """
    source_files_to_exclude = recursive_find_files(
        dependency_base_dir,
        EXCLUDE_INSTALLED_PACKAGES_GLOB,
    )
    return (
        source_file_path
        for source_file_path
        in find_solidity_source_files(dependency_base_dir)
        if not any(
            is_same_path(source_file_path, exclude_path)
            for exclude_path
            in source_files_to_exclude
        )
    )


@cast_return_to_tuple
def find_installed_package_locations(installed_packages_dir):
    """
    Return a tuple of all filesystem paths directly under the given
    `installed_packages_dir` that look like dependency base dirs.
    """
    if os.path.exists(installed_packages_dir):
        for maybe_package_dir in os.listdir(installed_packages_dir):
            dependency_base_dir = get_dependency_base_dir(
                installed_packages_dir,
                maybe_package_dir,
            )
            if is_dependency_base_dir(dependency_base_dir):
                yield dependency_base_dir


@cast_return_to_ordered_dict
def get_installed_dependency_locations(installed_packages_dir):
    for dependency_base_dir in find_installed_package_locations(installed_packages_dir):
        yield (
            extract_dependency_name_from_base_dir(dependency_base_dir),
            dependency_base_dir,
        )


@cast_return_to_tuple
def recursive_find_installed_dependency_base_dirs(installed_packages_dir):
    """
    Return a tuple of all filesystem paths directly under the given
    `installed_packages_dir` that look like dependency base dirs including all
    sub dependencies.
    """
    installed_package_locations = find_installed_package_locations(installed_packages_dir)
    for package_base_dir in installed_package_locations:
        yield package_base_dir
        sub_base_dirs = recursive_find_installed_dependency_base_dirs(package_base_dir)
        for sub_package_base_dir in sub_base_dirs:
            yield sub_package_base_dir


@cast_return_to_dict
def extract_build_dependendencies_from_installed_packages(installed_packages_dir):
    """
    Extract the current installed dependencies for creation of the
    `build_dependencies` section of a release lockfile.
    """
    installed_package_locations = find_installed_package_locations(installed_packages_dir)
    for dependency_base_dir in installed_package_locations:
        dependency_name = extract_dependency_name_from_base_dir(dependency_base_dir)
        dependency_identifier = get_build_identifier(dependency_base_dir)
        yield dependency_name, dependency_identifier
