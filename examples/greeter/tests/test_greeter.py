from populus.utils.transactions import (
    wait_for_transaction_receipt,
)


def test_greeter(chain):
    greeter = chain.get_contract('Greeter')

    greeting = greeter.call().greet()
    assert greeting == 'Hello'


def test_custom_greeting(web3, chain):
    greeter = chain.get_contract('Greeter')

    set_txn_hash = greeter.transact().setGreeting('Guten Tag')
    wait_for_transaction_receipt(web3, set_txn_hash)

    greeting = greeter.call().greet()
    assert greeting == 'Guten Tag'


def test_named_greeting(web3, chain):
    greeter = chain.get_contract('Greeter')

    greeting = greeter.call().greet('Piper')
    assert greeting == 'Hello Piper'
