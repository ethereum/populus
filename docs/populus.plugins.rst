Testing
=======

The Populus framework provides some powerful utilities for testing your
contracts.  Testing in Populus is powered by the python testing framework
``py.test``.


Quick Example
-------------

Lets write a test for the following simple contract.

.. code-block::

    # ./contracts/Math.sol
    contract Math {
            function add(int a, int b) public returns (int result){
                result = a + b;
                return result;
            }

            function multiply7(int a) public returns (int result){
                result = a * 7;
                return result;
            }

            function return13() public returns (int result) {
                result = 13;
                return result;
            }
    }

Populus expects to find tests in the ``./tests`` directory of your project.
The only naming requirement of the test module is that it must begin with
``test_`` so that it will be found by ``pytest``.

.. code-block::

    # ./tests/test_math.py

    def test_contracts_has_correct_functions(contracts):
        assert contracts.Math
        # Check that our contract has all of the expected functions.
        assert hasattr(contracts.Math, 'add')
        assert hasattr(contracts.Math, 'multiply7')
        assert hasattr(contracts.Math, 'return13')


    def test_contract_function_return_values(eth_coinbase, deployed_contracts):
        math = deployed_contracts.Math
        # Check that our functions compute the expected values.
        assert math.add.call(11, 12, _from=eth_coinbase) == 23
        assert math.multiply7.call(11, _from=eth_coinbase) == 77
        assert math.return13.call(_from=eth_coinbase) == 13


The code above declares two tests, ``test_contracts_has_correct_functions`` and
``test_contract_function_return_values``.  We can run these tests with the
``test`` command.


.. code-block:: shell

    $ populus test
    =================================== test session starts ===================================
    platform darwin -- Python 2.7.10 -- py-1.4.30 -- pytest-2.7.2 -- /usr/bin/python
    rootdir: /path/to/my-project, inifile: pytest.ini
    plugins: populus, capturelog, timeout
    collected 2 items

    tests/test_example.py::test_contracts_has_correct_functions PASSED
    tests/test_example.py::test_contract_function_return_values PASSED

    ================================ 2 passed in 0.82 seconds =================================

In the tests above, you may have noticed the use of the pytest fixtures
``eth_coinbase``, ``contracts`` and ``deployed_contracts``.  These are provided
by ``populus`` to help make testing contracts easier.


``pytest`` fixtures provided by Populus
---------------------------------------

The following fixtures are available for your tests.

``eth_coinbase`` - The ``coinbase`` account from ``ethereum.tester``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``hex`` encoded ``coinbase`` from the ``ethereum.tester`` module
provided by the ``pyethereum`` library.


``rpc_server`` - The testing ``JSON-RPC`` server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a ``JSON-RPC`` server running at ``127.0.0.1:8545``.  This server is
reset at the end of each test run.

The test server is from the ``eth-testrpc`` library.


``rpc_client`` - A client for interacting with a ``JSON-RPC`` server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A python client for the ``JSON-RPC`` server


``contracts`` - The compiled project contract classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An object with `~populus.contracts.BaseContract` classes for all of the
compiled contracts in your project.

.. note::

    Note that the contract code used in tests comes from the output from the
    ``compile`` command which means you must recompile your contracts for code
    changes to take effect in your tests.


``deployed_contracts`` - Deployed instances of your compiled contracts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deployed instances your contracts.  These contracts are deployed onto a
``testrpc`` server.
