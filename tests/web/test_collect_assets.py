import os

from populus.web import (
    get_build_assets_dir,
    collect_static_assets,
)


PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'projects', 'test-01'))


def test_collect_static_assets():
    collect_static_assets(PROJECT_DIR)

    expected_paths = (
        'js/contracts.js',
        'js/web3.js',
        'js/test-assets-dir.js',
        'js/sub-dir/test-assets-sub-dir.js',
        'top-dir/test-top-dir.txt',
    )

    build_assets_dir = get_build_assets_dir(PROJECT_DIR)

    for path in expected_paths:
        asset_path = os.path.join(build_assets_dir, path)
        assert os.path.exists(asset_path)
