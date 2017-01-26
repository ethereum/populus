Part 1: Basic Testing
=====================

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

    pragma solidity ^0.4.0;

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

    def test_greeter(chain):
        greeter = chain.get_contract('Greeter')

        greeting = greeter.call().greet()
        assert greeting == 'Hello'

    def test_custom_greeting(chain):
        greeter = chain.get_contract('Greeter')

        set_txn_hash = greeter.transact().setGreeting('Guten Tag')
        chain.wait.for_receipt(set_txn_hash)

        greeting = greeter.call().greet()
        assert greeting == 'Guten Tag'

    def test_named_greeting(chain):
        greeter = chain.get_contract('Greeter')

        greeting = greeter.call().greet('Piper')
        assert greeting == 'Hello Piper'


You can run tests using the ``py.test`` command line utility which was
installed when you installed populus.

.. code-block:: bash

    $ py.test tests/
    collected 3 items

    tests/test_greeter.py::test_greeter PASSED
    tests/test_greeter.py::test_custom_greeting PASSED
    tests/test_greeter.py::test_named_greeting PASSED

You should see something akin to the output above with three passing tests.
