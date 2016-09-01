Tutorial
========

.. contents:: :local:


Introduction
------------

The following tutorial picks up where the quickstart leaves off.  You should
have a single solidity contract named ``Greeter`` located in
``./contracts/Greeter.sol`` and a single test module
``./tests/test_greeter.py`` that contains two tests.


Modify our Greeter
------------------

Lets add way for the Greeter contract to greet someone by name.  We'll do so by
adding a new function ``greet(bytes name)`` which you can see below.  Update
your solidity source to match this updated version of the contract.


.. code-block:: solidity

    contract Greeter {
        string public greeting;

        function Greeter() {
            greeting = "Hello";
        }

        function setGreeting(string _greeting) public {
            greeting = _greeting;
        }

        function greet() constant returns (string) {
            return greeting;
        }

        function greet(bytes name) constant returns (bytes) {
            // create a byte array sufficiently large to store our greeting.
            bytes memory namedGreeting = new bytes(
                name.length + 1 + bytes(greeting).length
            );

            // push the greeting onto our return value.
            // greeting.
            for (uint i=0; i < bytes(greeting).length; i++) {
                namedGreeting[i] = bytes(greeting)[i];
            }

            // add a space before pushing the name on.
            namedGreeting[bytes(greeting).length] = ' ';

            // loop over the name and push all of the characters onto the
            // greeting.
            for (i=0; i < name.length; i++) {
                namedGreeting[bytes(greeting).length + 1 + i] = name[i];
            }
            return namedGreeting;
        }
    }


Testing our changes
-------------------

Now we'll want to test our contract.  Lets add another test to
``./tests/test_greeter.py`` so that the file looks as follows.

.. code-block:: python

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


Deploying the contract
----------------------

Since the ``Greeter`` contract is so simple, we can deploy it using the ``$
populus deploy`` command.  Lets deploy the contract to a local test chain.  We
can use the ``$ populus chain config`` command to setup the chain via an
interactive prompt.

.. code-block:: shell

    $ populus chain config local_test
    Configuring **new** chain: local_test
    -------------------------------------


    Populus can run the blockchain client for you, including connecting to the public main and test networks.

     Should populus manage running this chain? [Y/n]: y


    Web3 Provider Choices:
    1) IPC socket (default)
    2) RPC via HTTP

    How should populus connect web3.py to this chain? [ipc]: ipc


    Will this blockchain be running with a non-standard `geth.ipc`path?

     [y/N]: n
    This chain will default to sending transactions from 0xeb4036b556275f55a1a7e3cabda93df317f37459.  Would you like to set a different default account? [y/N]: n
    Writing configuration to populus.ini ...
    Success!

Now lets deploy our contract.

.. code-block:: shell

    $ populus deploy Greeter --chain local_test
    Accounts
    -----------------
    0 - 0xeb4036b556275f55a1a7e3cabda93df317f37459

    Enter the account address or the number of the desired account [0xeb4036b556275f55a1a7e3cabda93df317f37459]:
    Would you like set the address '0xeb4036b556275f55a1a7e3cabda93df317f37459' as the default`deploy_from` address for the 'local_test' chain? [y/N]: y
    Wrote updated chain configuration to 'populus.ini'
    Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).

    Greeter
    Deploying Greeter
    Deploy Transaction Sent: 0xb0864c64ed4fc6ef77ff7e747b4bc8db3f1ac235ea2d78a9f2bcf07b95f97115
    Waiting for confirmation...

    Transaction Mined
    =================
    Tx Hash      : 0xb0864c64ed4fc6ef77ff7e747b4bc8db3f1ac235ea2d78a9f2bcf07b95f97115
    Address      : 0x0b9539f881c846b13978c91d0e83730796dc9873
    Gas Provided : 655977
    Gas Used     : 555977


    Verifying deployed bytecode...
    Verified contract bytecode @ 0x0b9539f881c846b13978c91d0e83730796dc9873 matches expected runtime bytecode
    Deployment Successful.


Lets take a minute to discuss what just occurred *under the hood*.

First we configured a new private blockchain that we can use for testing.  This
is a **real** Ethereum blockchain in the sense that it will use the go-ethereum
binary to run the blockchain, and that you can interact with it the same way
you woult the public networks.

Next, we used the ``deploy`` command to deploy our ``Greeter`` contract onto
this blockchain.  Under the hood, Populus did the following things.

* Ran the test chain in a subprocess.
* Compiled your contracts.
* Sent the deploy transaction and waited for it to be mined.
* Verified that the deployment was successful by checking the on-chain bytecode
  against the expected value.
