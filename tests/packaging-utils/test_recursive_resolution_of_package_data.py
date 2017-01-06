from populus.utils.packaging import (
    compute_identifier_tree,
    flatten_identifier_tree,
    recursively_resolve_package_data,
)


def test_package_data_resolution_on_owned_example_package(load_example_project,
                                                          mock_package_backends):
    load_example_project('owned')
    lineages = flatten_identifier_tree(compute_identifier_tree(['owned'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(lineages[0], mock_package_backends)
    package_meta = package_data['meta']

    assert package_meta['version'] == '1.0.0'
    assert package_meta['dependency_name'] == 'owned'
    assert package_meta['package_name'] == 'owned'
    assert package_meta['install_identifier'] == 'owned==1.0.0'
    assert package_meta['build_identifier'] == 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND'

    assert not package_data['dependencies']
    assert './contracts/owned.sol' in package_data['source_tree']
