import pytest

from populus.compilation import (
    check_if_matches_filter,
)


@pytest.mark.parametrize(
    ('file_path_filter,contract_filter,file_path,contract_name,result'),
    (
        # single arg contract
        ('Example', 'Example', '/var/project/contracts/Example.sol', 'Example', True),
        ('Example', 'Example', '/var/project/contracts/Example.sol', 'NotExample', False),
        # single arg file path
        ('Example.sol', 'Example.sol', '/var/project/contracts/Example.sol', 'Example', True),
        ('contracts/Example.sol', 'contracts/Example.sol', '/var/project/contracts/Example.sol', 'Example', True),
        ('/var/project/contracts/Example.sol', '/var/project/contracts/Example.sol', '/var/project/contracts/Example.sol', 'Example', True),
        ('Example.sol', 'Example.sol', '/var/project/contracts/NotExample.sol', 'Example', False),
        # both args
        ('Example.sol', 'Example', '/var/project/contracts/Example.sol', 'Example', True),
        ('contracts/Example.sol', 'Example', '/var/project/contracts/Example.sol', 'Example', True),
        ('/var/project/contracts/Example.sol', 'Example', '/var/project/contracts/Example.sol', 'Example', True),
        ('Example.sol', 'Example', '/var/project/contracts/NotExample.sol', 'Example', False),
        ('Example.sol', 'Example', '/var/project/contracts/Example.sol', 'NotExample', False),
        ('contracts/Example.sol', 'Example', '/var/project/contracts/Example.sol', 'NotExample', False),
        ('/var/project/contracts/Example.sol', 'Example', '/var/project/contracts/Example.sol', 'NotExample', False),
    ),
)
def test_contract_only_matches(file_path_filter, contract_filter, file_path,
                               contract_name, result):
    assert check_if_matches_filter(
        file_path_filter, contract_filter, file_path, contract_name,
    ) is result
