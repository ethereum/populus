from populus.migrations import (
    SendTransaction,
)


def test_send_transaction_operation(web3, chain):
    send_transaction_operation = SendTransaction({
        'from': web3.eth.coinbase,
        'to': web3.eth.accounts[1],
        'value': 12345,
    }, timeout=30)

    initial_balance = web3.eth.getBalance(web3.eth.accounts[1])

    send_transaction_operation.execute(chain=chain)

    after_balance = web3.eth.getBalance(web3.eth.accounts[1])

    assert after_balance - initial_balance == 12345
