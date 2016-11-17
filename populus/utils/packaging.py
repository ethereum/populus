import os
import hashlib
import functools
import operator
import re
import json

import semver

from web3.utils.string import (
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
)


SUPPORTED_PACKAGE_MANIFEST_VERSIONS = {'1'}


PACKAGE_MANIFEST_FILENAME = './epm.json'


def get_project_package_manifest_path(project_dir):
    return os.path.join(project_dir, PACKAGE_MANIFEST_FILENAME)


def get_package_manifest_path(package_base_dir):
    return os.path.join(package_base_dir, PACKAGE_MANIFEST_FILENAME)


INSTALLED_PACKAGES_BASE_DIRNAME = './installed_packages'


def get_installed_packages_dir(base_dir):
    return os.path.join(base_dir, INSTALLED_PACKAGES_BASE_DIRNAME)


def get_package_base_dir(installed_packages_dir, package_name):
    package_base_dir = os.path.join(installed_packages_dir, package_name)
    return package_base_dir


def extract_dependency_name_from_package_base_dir(package_base_dir):
    return os.path.basename(package_base_dir.rstrip('/'))


RELEASE_LOCKFILE_FILENAME = 'lock.json'


def get_release_lockfile_path(package_base_dir):
    return os.path.join(package_base_dir, RELEASE_LOCKFILE_FILENAME)


ROOT_IDENTIFIER_LOCKFILE_NAME = 'root_identifier.lock'


def get_root_identifier_lockfile_path(package_base_dir):
    root_identifier_lockfile_path = os.path.join(
        package_base_dir,
        ROOT_IDENTIFIER_LOCKFILE_NAME,
    )
    return root_identifier_lockfile_path


RESOLVED_IDENTIFIER_LOCKFILE_NAME = 'resolved_identifier.lock'


def get_resolved_identifier_lockfile_path(package_base_dir):
    resolved_identifier_lockfile_path = os.path.join(
        package_base_dir,
        RESOLVED_IDENTIFIER_LOCKFILE_NAME,
    )
    return resolved_identifier_lockfile_path


RELEASE_LOCKFILE_BUILD_FILENAME = '{version}.json'


def get_lockfile_build_path(build_asset_dir, version_string):
    filename = RELEASE_LOCKFILE_BUILD_FILENAME.format(version=version_string)
    release_lockfile_build_path = os.path.join(build_asset_dir, filename)
    return release_lockfile_build_path


def is_package_base_dir(directory_path):
    release_lockfile_path = get_release_lockfile_path(directory_path)
    return os.path.exists(release_lockfile_path)


def get_installed_package_version(package_base_dir):
    release_lockfile_path = get_release_lockfile_path(package_base_dir)
    with open(release_lockfile_path) as release_lockfile_file:
        release_lockfile = json.load(release_lockfile_file)
    return release_lockfile['version']


def get_resolved_identifier(package_base_dir):
    resolved_identifier_lockfile_path = get_resolved_identifier_lockfile_path(package_base_dir)
    with open(resolved_identifier_lockfile_path) as resolved_identifier_lockfile_file:
        resolved_identifier = resolved_identifier_lockfile_file.read().strip()
    return resolved_identifier


def create_contract_instance_object(contract_name,
                                    address=None,
                                    deploy_transaction=None,
                                    deploy_block=None,
                                    contract_data=None,
                                    link_dependencies=None):
    if contract_data is None:
        contract_data = {}

    contract_instance_data = {
        'contract_name': contract_name,
    }

    if 'bytecode' in contract_data:
        contract_instance_data['bytecode'] = contract_data['bytecode']
    if 'runtime_bytecode' in contract_data:
        contract_instance_data['runtime_bytecode'] = contract_data['runtime_bytecode']
    if 'abi' in contract_data:
        contract_instance_data['abi'] = contract_data['abi']
    if 'natspec' in contract_data:
        contract_instance_data['natspec'] = contract_data['natspec']

    if 'compiler' in contract_data:
        contract_instance_data['compiler'] = contract_data['compiler']
    elif 'bytecode' in contract_instance_data or 'runtime_bytecode' in contract_instance_data:
        raise ValueError(
            'Compiler information must be specified if either bytecode or '
            'runtime bytecode are included'
        )

    if link_dependencies:
        # TODO: this needs to be massaged into the correct format.
        contract_instance_data['link_dependencies'] = link_dependencies

    return contract_instance_data


CONTRACT_NAME_REGEX = '^[_a-zA-Z][_a-zA-Z0-9]*$'


def is_contract_name(value):
    return bool(re.match(CONTRACT_NAME_REGEX, value))


PACKAGE_NAME_REGEX = '[a-z][-a-z0-9]{0,213}'

EXACT_PACKAGE_NAME_REGEX = (
    "^"
    "{package_name_regex}"
    "$"
).format(
    package_name_regex=PACKAGE_NAME_REGEX,
)


def is_package_name(value):
    return bool(re.match(EXACT_PACKAGE_NAME_REGEX, value))


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


def is_dependency_version(value):
    return bool(re.match(DEPENDENCY_VERSION_REGEX, value))


EXACT_VERSION_REGEX = (
    "^"
    "(?P<version>{version_number_regex})"
    "$"
).format(
    version_number_regex=VERSON_NUMBER_REGEX,
)


def is_exact_version(value):
    return bool(re.match(EXACT_VERSION_REGEX, value))


def is_local_project_package_identifier(project_dir, package_identifier):
    if not os.path.exists(package_identifier):
        return False
    return is_same_path(package_identifier, project_dir)


def is_aliased_ipfs_uri(value):
    dependency_name, _, maybe_ipfs_uri = value.partition('@')
    return all((
        is_package_name(dependency_name),
        is_ipfs_uri(maybe_ipfs_uri)
    ))


def is_filesystem_release_lockfile_path(package_identifier):
    if not os.path.exists(package_identifier):
        return False
    elif not os.path.isfile(package_identifier):
        return False

    with open(package_identifier) as maybe_release_lockfile_file:
        try:
            maybe_release_lockfile = json.load(maybe_release_lockfile_file)
        except json.JSONDecodeError:
            return False

    validate_release_lockfile(maybe_release_lockfile)

    return True


def is_aliased_filesystem_release_lockfile_path(package_identifier):
    dependency_name, _, maybe_release_lockfile_path = package_identifier.partition('@')
    return all((
        is_package_name(dependency_name),
        is_filesystem_release_lockfile_path(maybe_release_lockfile_path),
    ))


def parse_package_identifier(value):
    match = re.match(PACKAGE_IDENTIFIER_REGEX, value)
    if match is None:
        raise ValueError("Unsupported package identifier format: {0}".format(value))
    parts = match.groupdict()
    return parts['package_name'], parts['version_comparison'], parts['version']


def construct_dependency_identifier(dependency_name, identifier):
    if is_direct_package_identifier(identifier):
        return "{dependency_name}:{package_identifier}".format(
            dependency_name=dependency_name,
            package_identifier=identifier,
        )
    elif is_ipfs_uri(identifier):
        return "{dependency_name}@{ipfs_uri}".format(
            dependency_name=dependency_name,
            ipfs_uri=identifier,
        )
    elif is_dependency_version(identifier):
        if is_exact_version:
            return "{dependency_name}=={version}".format(
                dependency_name=dependency_name,
                version=identifier,
            )
        else:
            return "{dependency_name}{version}".format(
                dependency_name=dependency_name,
                version=identifier,
            )
    else:
        raise ValueError("Unsupported Identifier: '{0}'".format(identifier))


def extract_dependency_name_from_identifier_lineage(package_identifier_lineage,
                                                    release_lockfile):
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
    # TODO: implement jsonschema validation
    pass


def validate_release_lockfile(package_manifest):
    # TODO: implement jsonschema validation
    pass


@cast_return_to_tuple
def translate_dependencies_to_package_identifiers(dependencies):
    for package_name, dependency_identifier in dependencies.items():
        if is_dependency_version(dependency_identifier):
            if is_exact_version(dependency_identifier):
                yield "{package_name}=={version}".format(
                    package_name=package_name,
                    version=dependency_identifier,
                )
            else:
                yield "{package_name}{dependency_identifier}".format(
                    package_name=package_name,
                    dependency_identifier=dependency_identifier,
                )
        elif is_ipfs_uri(dependency_identifier):
            yield dependency_identifier
        else:
            raise ValueError(
                "Invalid dependency identifier: '{0}'".format(dependency_identifier)
            )


def extract_root_identifier(package_identifier_lineage):
    for identifier in package_identifier_lineage:
        if is_package_name(identifier):
            return identifier
        elif is_direct_package_identifier(identifier):
            return identifier
        elif is_ipfs_uri(identifier):
            return identifier
        elif is_filesystem_release_lockfile_path(identifier):
            return identifier
    else:
        raise ValueError("No valid root identifiers found in package identifier lineage")


def extract_package_metadata(package_identifier_lineage,
                             release_lockfile):
    return {
        'version': release_lockfile['version'],
        'package_name': release_lockfile['package_name'],
        'dependency_name': extract_dependency_name_from_identifier_lineage(
            package_identifier_lineage,
            release_lockfile,
        ),
        'root_identifier': extract_root_identifier(package_identifier_lineage),
        'resolved_identifier': package_identifier_lineage[-1],
    }


def translate_package_identifier(package_identifier, package_backends):
    for backend in package_backends.values():
        if backend.can_translate_package_identifier(package_identifier):
            return backend.translate_package_identifier(package_identifier)
    else:
        raise ValueError(
            "No package backends are able to translate the identifier: "
            "{0}".format(package_identifier)
        )


def fingerprint_identifier(package_identifier):
    return hashlib.md5(force_bytes(package_identifier)).hexdigest()


@cast_return_to_dict
def compute_translated_identifier_tree(identifier_set,
                                       package_backends,
                                       seen_fingerprints=None):
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
                compute_translated_identifier_tree(
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
def flatten_translated_identifier_tree(identifier_tree):
    for key, value in identifier_tree.items():
        if value is None:
            yield (key,)
        else:
            for sub_value in flatten_translated_identifier_tree(value):
                yield (key,) + sub_value


def resolve_to_release_lockfile(package_identifier, package_backends):
    for _, backend in package_backends.items():
        if backend.can_resolve_to_release_lockfile(package_identifier):
            return backend.resolve_to_release_lockfile(package_identifier)
        else:
            continue
    else:
        raise ValueError(
            "None of the configured package backends support resolving the "
            "identifier '{0}'".format(package_identifier)
        )


def resolve_package_source_tree(release_lockfile, package_backends):
    for _, backend in package_backends.items():
        if backend.can_resolve_package_source_tree(release_lockfile):
            return backend.resolve_package_source_tree(release_lockfile)
        else:
            continue
    else:
        raise ValueError(
            "None of the configured package backends could resolve the source tree for"
            "'{0}'".format(release_lockfile)
        )


def recursively_resolve_package_data(package_identifier_lineage, package_backends):
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

    dependency_identifiers = translate_dependencies_to_package_identifiers(
        release_lockfile.get('build_dependencies', {})
    )
    dependency_identifier_tree = compute_translated_identifier_tree(
        dependency_identifiers,
        package_backends,
    )
    flattened_dependency_identifier_tree = flatten_translated_identifier_tree(
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
    return {
        version
        for version
        in all_versions
        if is_version_match(version, version_target)
    }


def get_max_version(all_versions):
    if not all_versions:
        raise ValueError('Must pass in at least 1 version string.')
    return functools.reduce(semver.max_ver, all_versions)


EXCLUDE_INSTALLED_PACKAGES_GLOB = "./installed_packages/*"


@cast_return_to_tuple
def find_package_source_files(package_base_dir):
    source_files_to_exclude = recursive_find_files(
        package_base_dir,
        EXCLUDE_INSTALLED_PACKAGES_GLOB,
    )
    return (
        source_file_path
        for source_file_path
        in find_solidity_source_files(package_base_dir)
        if not any(
            is_same_path(source_file_path, exclude_path)
            for exclude_path
            in source_files_to_exclude
        )
    )


@cast_return_to_tuple
def find_installed_package_locations(installed_packages_dir):
    if os.path.exists(installed_packages_dir):
        for maybe_package_dir in os.listdir(installed_packages_dir):
            package_base_dir = os.path.join(installed_packages_dir, maybe_package_dir)
            if is_package_base_dir(package_base_dir):
                yield package_base_dir


@cast_return_to_tuple
def recursive_find_installed_package_base_dirs(installed_packages_dir):
    installed_package_locations = find_installed_package_locations(installed_packages_dir)
    for package_base_dir in installed_package_locations:
        yield package_base_dir
        for sub_package_base_dir in recursive_find_installed_package_base_dirs(package_base_dir):
            yield sub_package_base_dir


@cast_return_to_dict
def extract_build_dependendencies_from_installed_packages(installed_packages_dir):
    installed_package_locations = find_installed_package_locations(installed_packages_dir)
    for package_base_dir in installed_package_locations:
        dependency_name = extract_dependency_name_from_package_base_dir(package_base_dir)
        dependency_identifier = get_resolved_identifier(package_base_dir)
        # TODO: handle duplicate dependency names.
        yield dependency_name, dependency_identifier
