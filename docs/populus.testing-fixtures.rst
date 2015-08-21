pytest fixtures provided by Populus
=======================================

The following fixtures are available for your tests.

``eth_coinbase`` - The ``coinbase`` account from ``ethereum.tester``
--------------------------------------------------------------------

The ``hex`` encoded ``coinbase`` from the ``ethereum.tester`` module
provided by the ``pyethereum`` library.


``rpc_server`` - The testing ``JSON-RPC`` server
------------------------------------------------

Provides a ``JSON-RPC`` server running at ``127.0.0.1:8545``.  This server is
reset at the end of each test run.

The test server is from the ``eth-testrpc`` library.


``rpc_client`` - A client for interacting with a ``JSON-RPC`` server
--------------------------------------------------------------------

A python client for the ``JSON-RPC`` server


``contracts`` - The compiled project contract classes
-----------------------------------------------------

An object with `~populus.contracts.BaseContract` classes for all of the
compiled contracts in your project.

.. note::

    Note that the contract code used in tests comes from the output from the
    ``compile`` command which means you must recompile your contracts for code
    changes to take effect in your tests.


``deployed_contracts`` - Deployed instances of your compiled contracts
----------------------------------------------------------------------

Deployed instances your contracts.  These contracts are deployed onto a
``testrpc`` server.
