import pytest

from populus.utils.testing import (
    load_contract_fixture,
)


@load_contract_fixture('Simple.sol')
def test_chain_get_contract_factories_raises_deprecation_warnings(chain):
    with pytest.warns(DeprecationWarning):
        chain.get_contract_factory('Simple')


@load_contract_fixture('Simple.sol')
def test_chain_get_contract_factories_with_link_dependencies_raises_deprecation_warnings(chain):
    with pytest.warns(DeprecationWarning) as record:
        with pytest.raises(DeprecationWarning):
            chain.get_contract_factory('Simple', link_dependencies={
                'Foo': '0xd3cda913deb6f67967b99d67acdfa1712c293601',
            })


def test_contract_factories_property_raises_deprecation_warning(chain):
    with pytest.warns(DeprecationWarning):
        chain.contract_factories


@load_contract_fixture('Simple.sol')
def test_is_contract_available_raises_deprecation_warning(chain):
    with pytest.warns(DeprecationWarning):
        chain.is_contract_available('Simple')


@load_contract_fixture('Simple.sol')
def test_is_contract_available_with_extra_args_raises_deprecation_warnings(chain):
    with pytest.warns(DeprecationWarning):
        with pytest.raises(DeprecationWarning):
            chain.is_contract_available('Simple', link_dependencies={
                'Foo': '0xd3cda913deb6f67967b99d67acdfa1712c293601',
            })


@load_contract_fixture('Simple.sol')
def test_get_contract_raises_deprecation_warnings(chain):
    chain.provider.deploy_contract('Simple')

    with pytest.warns(DeprecationWarning):
        chain.get_contract('Simple')


def test_get_contract_raises_deprecation_warnings(chain):
    with pytest.warns(DeprecationWarning):
        chain.deployed_contracts
