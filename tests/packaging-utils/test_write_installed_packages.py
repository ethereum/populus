from populus import Project

from populus.utils.filesystem import (
    ensure_file_exists,
    ensure_path_exists,
)
from populus.utils.packaging import (
    compute_identifier_tree,
    flatten_identifier_tree,
    recursively_resolve_package_data,
)

from populus.packages import (
    write_installed_packages,
    write_package_files,
)


def test_writing_project_installed_packages(project_dir,
                                            write_project_file,
                                            load_example_project,
                                            mock_package_backends):
    load_example_project('owned')
    load_example_project('safe-math-lib')
    load_example_project('wallet')
    lineages = flatten_identifier_tree(compute_identifier_tree(['wallet'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(lineages[0], mock_package_backends)

    project = Project

    pre_existing_file_path = os.path.join(project.installed_packages_dir, 'test-file.txt')
    ensure_file_exists(pre_existing_file_path, 'test-this-is-not-overridden')

    pre_existing_dir_path = os.path.join(project.installed_packages_dir, 'test-dir')
    ensure_dir_exists(pre_existing_dir)
    ensure_file_exists(os.path.join(pre_existing_dir, 'is-present'))

    assert False, 'WIP'
