Testing
=======

.. contents:: :local:

Introduction
------------

The Populus framework provides some powerful utilities for testing your
contracts.  Testing in Populus is powered by the python testing framework
``py.test``.

Your tests can be run against any of the various chains that Populus supports,
including test chains backed by the go-ethereum client, the eth-testrpc EVM
backed by the ``pyethereum.tester`` EVM, or even the public ethereum networks
if you were to so choose.


Quick Example
-------------

Lets write a test for the following simple contract.

::

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

While you may locate your tests anywhere you would like, Populus projects
default to using the ``./tests`` directory.  Test files within this directory
need to be valid python modules that begin with ``test_`` in order for
``py.test`` to find them.

::

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

    $ py.test -v
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


Creating new accounts
---------------------

You might want to create new Geth accounts to test ETH transfers between accounts and your contracts. Populus internally uses `PyGeth <https://github.com/pipermerriam/py-geth>`_ library for Geth account management.

Example (Python 3):

.. code-block:: python

    import pytest

    from eth_rpc_client import Client
    from geth.accounts import create_new_account


    @pytest.fixture
    def target_account(client: Client) -> str:
        """Create external, non-database Ethereum account, that can be used as a withdrawal target.

        :return: 0x address of the account
        """

        # We store keystore files in the current working directory
        # of the test run
        data_dir = os.getcwd()
        account = create_new_account(data_dir, password="")
        return account


