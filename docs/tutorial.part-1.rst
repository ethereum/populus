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
        greeter, _ = chain.provider.get_or_deploy_contract('Greeter')

        greeting = greeter.call().greet()
        assert greeting == 'Hello'

    def test_custom_greeting(chain):
        greeter, _ = chain.provider.get_or_deploy_contract('Greeter')

        set_txn_hash = greeter.transact().setGreeting('Guten Tag')
        chain.wait.for_receipt(set_txn_hash)

        greeting = greeter.call().greet()
        assert greeting == 'Guten Tag'

    def test_named_greeting(chain):
        greeter, _ = chain.provider.get_or_deploy_contract('Greeter')

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

Behind the scenes, populus uses a pytest plugin that creates a populus project object, and then provide this object,
(and it's derived objects), to the test functions via a pytest fixture.

Thus, tests run for a specific project.

If you run py.test from within the project directory, populus will assume that the current working directory
is the project you want to test, and the fixtures will be based on this directory.

The same is true if you provide pytest one positional argument for testing, which is the project directory:

.. code-block:: bash

    $ py.test /path/to/my/project/

Here, populus will provide the fixtures based on the project at ``/path/to/my/project/``. Pytest will also find the tests in that directory.
Note that populus and py.test look for their files separatly. Pytest looks for and collects the tests, populus for the the populus.json and other project files.


When you want to run tests that are saved outside the project directory, you will have to explictly provide the project directory.
If the tests are at ``/path/to/tests/``, then you can set the tested *project* directory as follows:

1. As a command line argument: ``$ py.test /path/to/tests/ --populus-project /path/to/my/project/``
2. In a pytest.ini file, with the following entry: ``populus_project=/path/to/my/project/``
3. With an environment variable: ``PYTEST_POPULUS_PROJECT``. E.g., ``$ export PYTEST_POPULUS_PROJECT=/path/to/my/project/``

If you used method 2 or 3, that is with pytest.ini or an environment variable, then:

.. code-block:: bash

    $ py.test /path/to/tests/

Will do, and populus will figure out the testing project from pytest.ini or the environment variable. The tests found at
``/path/to/tests/`` will be applied to this project.

.. note::

    For pytest.ini files, make sure the file is in the right location, and that py.test actually picks it.
    See https://docs.pytest.org/en/latest/customize.html#initialization-determining-rootdir-and-inifile .

So by providing explicit project for testing, you can run tests from one project on another, or if all your projects
provide a repeating functionality, you can use the same set of tests for all of them.

