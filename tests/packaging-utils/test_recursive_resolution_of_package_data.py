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


def test_package_data_resolution_on_transferable_example_package(load_example_project,
                                                                 mock_package_backends):
    load_example_project('owned')
    load_example_project('transferable')
    lineages = flatten_identifier_tree(compute_identifier_tree(['transferable'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(lineages[0], mock_package_backends)
    package_meta = package_data['meta']

    assert package_meta['version'] == '1.0.0'
    assert package_meta['dependency_name'] == 'transferable'
    assert package_meta['package_name'] == 'transferable'
    assert package_meta['install_identifier'] == 'transferable==1.0.0'
    assert package_meta['build_identifier'] == 'ipfs://QmaTMa6MwtH6CisPypiFkFdd1ByrFAvdExcQkUQwqbMeZx'

    assert './contracts/transferable.sol' in package_data['source_tree']
    assert len(package_data['dependencies'])

    owned_package_data = package_data['dependencies'][0]
    owned_package_meta = owned_package_data['meta']

    assert owned_package_meta['version'] == '1.0.0'
    assert owned_package_meta['dependency_name'] == 'owned'
    assert owned_package_meta['package_name'] == 'owned'
    assert owned_package_meta['install_identifier'] == 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND'
    assert owned_package_meta['build_identifier'] == 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND'

    assert not owned_package_data['dependencies']
    assert './contracts/owned.sol' in owned_package_data['source_tree']


def test_package_data_resolution_on_standard_token_example_package(load_example_project,
                                                          mock_package_backends):
    load_example_project('standard-token')
    lineages = flatten_identifier_tree(compute_identifier_tree(['standard-token'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(lineages[0], mock_package_backends)
    package_meta = package_data['meta']

    assert package_meta['version'] == '1.0.0'
    assert package_meta['dependency_name'] == 'standard-token'
    assert package_meta['package_name'] == 'standard-token'
    assert package_meta['install_identifier'] == 'standard-token==1.0.0'
    assert package_meta['build_identifier'] == 'ipfs://QmegJYswSDXUJbKWBuTj7AGBY15XceKxnF1o1Vo2VvVPLQ'

    assert not package_data['dependencies']
    assert './contracts/AbstractToken.sol' in package_data['source_tree']
    assert './contracts/StandardToken.sol' in package_data['source_tree']


def test_package_data_resolution_on_piper_coin_example_package(load_example_project,
                                                               mock_package_backends):
    load_example_project('standard-token')
    load_example_project('piper-coin')
    lineages = flatten_identifier_tree(compute_identifier_tree(['piper-coin'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(lineages[0], mock_package_backends)
    package_meta = package_data['meta']

    assert package_meta['version'] == '1.0.0'
    assert package_meta['dependency_name'] == 'piper-coin'
    assert package_meta['package_name'] == 'piper-coin'
    assert package_meta['install_identifier'] == 'piper-coin==1.0.0'
    assert package_meta['build_identifier'] == 'ipfs://QmYxRT4k5ByUH4N4A455M5s1RxsgUfqyYrntcuuxdHezXv'

    assert not package_data['source_tree']

    assert len(package_data['dependencies']) == 1

    standard_token_package_data = package_data['dependencies'][0]
    standard_token_package_meta = standard_token_package_data['meta']

    assert standard_token_package_meta['version'] == '1.0.0'
    assert standard_token_package_meta['dependency_name'] == 'standard-token'
    assert standard_token_package_meta['package_name'] == 'standard-token'
    assert standard_token_package_meta['install_identifier'] == 'ipfs://QmegJYswSDXUJbKWBuTj7AGBY15XceKxnF1o1Vo2VvVPLQ'
    assert standard_token_package_meta['build_identifier'] == 'ipfs://QmegJYswSDXUJbKWBuTj7AGBY15XceKxnF1o1Vo2VvVPLQ'

    assert not standard_token_package_data['dependencies']
    assert './contracts/AbstractToken.sol' in standard_token_package_data['source_tree']
    assert './contracts/StandardToken.sol' in standard_token_package_data['source_tree']


def test_package_data_resolution_on_safe_math_lib_example_package(load_example_project,
                                                                  mock_package_backends):
    load_example_project('safe-math-lib')
    lineages = flatten_identifier_tree(compute_identifier_tree(['safe-math-lib'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(lineages[0], mock_package_backends)
    package_meta = package_data['meta']

    assert package_meta['version'] == '1.0.0'
    assert package_meta['dependency_name'] == 'safe-math-lib'
    assert package_meta['package_name'] == 'safe-math-lib'
    assert package_meta['install_identifier'] == 'safe-math-lib==1.0.0'
    assert package_meta['build_identifier'] == 'ipfs://QmfUwis9K2SLwnUh62PDb929JzU5J2aFKd4kS1YErYajdq'

    assert not package_data['dependencies']
    assert './contracts/SafeMathLib.sol' in package_data['source_tree']


def test_package_data_resolution_on_escrow_example_package(load_example_project,
                                                           mock_package_backends):
    load_example_project('escrow')
    lineages = flatten_identifier_tree(compute_identifier_tree(['escrow'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(lineages[0], mock_package_backends)
    package_meta = package_data['meta']

    assert package_meta['version'] == '1.0.0'
    assert package_meta['dependency_name'] == 'escrow'
    assert package_meta['package_name'] == 'escrow'
    assert package_meta['install_identifier'] == 'escrow==1.0.0'
    assert package_meta['build_identifier'] == 'ipfs://Qmb4YtjwsAQyYXmCwSF71Lez9d7qchPc6WkT2iGc9m1gX6'

    assert not package_data['dependencies']
    assert './contracts/Escrow.sol' in package_data['source_tree']
    assert './contracts/SafeSendLib.sol' in package_data['source_tree']


def test_package_data_resolution_on_wallet_example_package(load_example_project,
                                                           mock_package_backends):
    load_example_project('owned')
    load_example_project('safe-math-lib')
    load_example_project('wallet')
    lineages = flatten_identifier_tree(compute_identifier_tree(['wallet'], mock_package_backends))
    assert len(lineages) == 1

    package_data = recursively_resolve_package_data(lineages[0], mock_package_backends)
    package_meta = package_data['meta']

    assert package_meta['version'] == '1.0.0'
    assert package_meta['dependency_name'] == 'wallet'
    assert package_meta['package_name'] == 'wallet'
    assert package_meta['install_identifier'] == 'wallet==1.0.0'
    assert package_meta['build_identifier'] == 'ipfs://QmSg2QvGhQrYgQqbTGVYjGmF9hkEZrxQNmSXsr8fFyYtD4'

    assert './contracts/Wallet.sol' in package_data['source_tree']

    assert len(package_data['dependencies']) == 2
    owned_package_data, safe_math_lib_package_data = tuple(sorted(
        package_data['dependencies'],
        key=lambda d: d['meta']['package_name']
    ))

    owned_package_meta = owned_package_data['meta']

    assert owned_package_meta['version'] == '1.0.0'
    assert owned_package_meta['dependency_name'] == 'owned'
    assert owned_package_meta['package_name'] == 'owned'
    assert owned_package_meta['install_identifier'] == 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND'
    assert owned_package_meta['build_identifier'] == 'ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND'

    assert not owned_package_data['dependencies']
    assert './contracts/owned.sol' in owned_package_data['source_tree']

    safe_math_lib_package_meta = safe_math_lib_package_data['meta']

    assert safe_math_lib_package_meta['version'] == '1.0.0'
    assert safe_math_lib_package_meta['dependency_name'] == 'safe-math-lib'
    assert safe_math_lib_package_meta['package_name'] == 'safe-math-lib'
    assert safe_math_lib_package_meta['install_identifier'] == 'ipfs://QmfUwis9K2SLwnUh62PDb929JzU5J2aFKd4kS1YErYajdq'
    assert safe_math_lib_package_meta['build_identifier'] == 'ipfs://QmfUwis9K2SLwnUh62PDb929JzU5J2aFKd4kS1YErYajdq'

    assert not safe_math_lib_package_data['dependencies']
    assert './contracts/SafeMathLib.sol' in safe_math_lib_package_data['source_tree']
