from populus.client import Client


def test_send_a_transaction(rpc_server, eth_tester):
    client = Client('127.0.0.1', '8545')

    from_addr = eth_tester.encode_hex(eth_tester.accounts[0])
    to_addr = eth_tester.encode_hex(eth_tester.accounts[1])

    txn_hash = client.send_transaction(
        _from=from_addr,
        to=to_addr,
        value=12345,
    )

    after_balance = client.get_balance(from_addr)

    assert after_balance == 1000004999999999999987655L


def test_contract_creation(rpc_server, eth_tester):
    client = Client('127.0.0.1', '8545')

    data = "0x60606040525b5b600a8060136000396000f30060606040526008565b00"
    from_addr = eth_tester.encode_hex(eth_tester.accounts[0])

    txn_hash = client.send_transaction(
        _from=from_addr,
        value=12345,
        data=data,
    )
    txn_receipt = client.get_transaction_receipt(txn_hash)
    contract_addr = txn_receipt['contractAddress']

    contract_balance = client.get_balance(contract_addr)
    assert contract_balance == 12345
