
import pytest

from eth_rpc_client import Client

from populus.contracts import (
    deploy_contract,
    get_contract_address_from_txn,
)

from ethereum import utils as ethereum_utils


def test_constructor_with_args(rpc_server, rpc_client, Named, eth_coinbase):
    deploy_txn_hash = deploy_contract(
        rpc_client,
        Named,
        constructor_args=("John",),
        _from=eth_coinbase,
    )
    contract_addr = get_contract_address_from_txn(rpc_client, deploy_txn_hash)

    named = Named(contract_addr)
    name = named.name.call(_from=eth_coinbase)
    assert name == "John"
