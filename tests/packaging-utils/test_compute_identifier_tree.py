import json
from populus.utils.packaging import (
    compute_identifier_tree,
)


def test_tree_computation_for_exact_package_name(mock_package_index_backend,
                                                 mock_package_backends):
    mock_package_index_backend.packages['owned'] = {
        '1.0.0': 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND',
    }
    identifier_tree = compute_identifier_tree(
        ['owned'],
        mock_package_backends,
    )
    expected = {
        'owned': {
            'owned==1.0.0': {
                'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND': None,
            },
        },
    }
    assert identifier_tree == expected


def test_tree_computation_for_aliased_exact_package_name(mock_package_index_backend,
                                                 mock_package_backends):
    mock_package_index_backend.packages['owned'] = {
        '1.0.0': 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND',
    }
    identifier_tree = compute_identifier_tree(
        ['powned:owned'],
        mock_package_backends,
    )
    expected = {
        'powned:owned': {
            'owned': {
                'owned==1.0.0': {
                    'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND': None,
                },
            },
        },
    }
    assert identifier_tree == expected


def test_tree_computation_for_exact_version_package_identifier(mock_package_index_backend,
                                                               mock_package_backends):
    mock_package_index_backend.packages['owned'] = {
        '1.0.0': 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND',
    }
    identifier_tree = compute_identifier_tree(
        ['owned==1.0.0'],
        mock_package_backends,
    )
    expected = {
        'owned==1.0.0': {
            'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND': None,
        },
    }
    assert identifier_tree == expected


def test_tree_computation_for_comparison_package_identifier(mock_package_index_backend,
                                                            mock_package_backends):
    mock_package_index_backend.packages['owned'] = {
        '1.0.0': 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND',
        '2.0.0': 'ipfs://QmPvJ1P9B5rh8ZsMqwkEhUjEVfaRA36sTD4JeyP1Mbo1Vh',
    }
    identifier_tree = compute_identifier_tree(
        ['owned>1.0.0'],
        mock_package_backends,
    )
    expected = {
        'owned>1.0.0': {
            'owned==2.0.0': {
                'ipfs://QmPvJ1P9B5rh8ZsMqwkEhUjEVfaRA36sTD4JeyP1Mbo1Vh': None,
            },
        },
    }
    assert identifier_tree == expected


def test_tree_computation_from_manifest_dependencies(project_dir,
                                                     write_project_file,
                                                     mock_package_index_backend,
                                                     mock_package_backends):
    mock_package_index_backend.packages['owned'] = {
        '1.0.0': 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND',
        '2.0.0': 'ipfs://QmPvJ1P9B5rh8ZsMqwkEhUjEVfaRA36sTD4JeyP1Mbo1Vh',
    }
    mock_package_index_backend.packages['standard-token'] = {
        '1.0.0': 'ipfs://QmegJYswSDXUJbKWBuTj7AGBY15XceKxnF1o1Vo2VvVPLQ',
    }

    package_manifest = {
        'package_name': 'test-package',
        'dependencies': {
            'owned': ">1.0.0",
            'standard-token': '1.0.0',
        }
    }
    write_project_file('ethpm.json', json.dumps(package_manifest))

    identifier_tree = compute_identifier_tree(
        ['.'],
        mock_package_backends,
    )
    expected = {
        '.': {
            'owned>1.0.0': {
                'owned==2.0.0': {
                    'ipfs://QmPvJ1P9B5rh8ZsMqwkEhUjEVfaRA36sTD4JeyP1Mbo1Vh': None,
                },
            },
            'standard-token==1.0.0': {
                'ipfs://QmegJYswSDXUJbKWBuTj7AGBY15XceKxnF1o1Vo2VvVPLQ': None,
            }
        }
    }
    assert identifier_tree == expected


def test_tree_computation_from_release_lockfile(project_dir,
                                                write_project_file,
                                                mock_package_index_backend,
                                                mock_package_backends):
    release_lockfile = {
        'lockfile_version': '1',
        'version': '1.0.0',
        'package_name': 'test-package',
    }
    write_project_file('test-package-1.0.0.json', json.dumps(release_lockfile))

    identifier_tree = compute_identifier_tree(
        ['test-package-1.0.0.json'],
        mock_package_backends,
    )
    expected = {
        'test-package-1.0.0.json': None,
    }
    assert identifier_tree == expected


def test_tree_computation_from_aliased_release_lockfile(project_dir,
                                                        write_project_file,
                                                        mock_package_index_backend,
                                                        mock_package_backends):
    release_lockfile = {
        'lockfile_version': '1',
        'version': '1.0.0',
        'package_name': 'test-package',
    }
    write_project_file('test-package-1.0.0.json', json.dumps(release_lockfile))

    identifier_tree = compute_identifier_tree(
        ['aliased-test-package@test-package-1.0.0.json'],
        mock_package_backends,
    )
    expected = {
        'aliased-test-package@test-package-1.0.0.json': {
            'test-package-1.0.0.json': None,
        }
    }
    assert identifier_tree == expected
