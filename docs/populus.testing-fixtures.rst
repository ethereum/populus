pytest fixtures provided by Populus
=======================================

The following fixtures are available for your tests.

``test_coinbase`` - The ``coinbase`` account from ``ethereum.tester``
--------------------------------------------------------------------

The ``hex`` encoded ``coinbase`` from the ``ethereum.tester`` module
provided by the ``pyethereum`` library.


``rpc_server`` - The testing ``JSON-RPC`` server
------------------------------------------------

Provides a ``JSON-RPC`` server running at ``127.0.0.1:8545``.  This server is
reset at the end of each test run.

The test server is from the ``eth-testrpc`` library.

The server can be configured to run on a different host or port by setting the
following variables at the top level of your module.

* ``rpc_host`` - default: ``'127.0.0.1'```
* ``rpc_port`` - default: ``'8545'```


``rpc_client`` - A client for interacting with a ``JSON-RPC`` server
--------------------------------------------------------------------

A python client for the ``JSON-RPC`` server.  The hostname and port can be
configuered by setting the following variable at the top level of your python
module.

* ``rpc_host`` - default: ``'127.0.0.1'```
* ``rpc_port`` - default: ``'8545'```


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

Deployed instances your contracts.

To use this fixture, you must also have a valid JSON RPC server running.  This
can be accomplished by including either of ``rpc_server`` or ``geth_node``
fixtures in your test case.


``geth_node`` - A running ``geth`` node.
----------------------------------------

This is a module level fixture that has a geth node running against the test
chain at ``./chains/default-test/``.

This fixture can be configured by setting the following variables at the top
level of the module in which you are using this fixture.

* ``geth_project_dir`` - The path that should be considered the root of your
  project.  Default: ``os.getcwd()``.
* ``geth_chain_name`` - The name of the test chain that should be used.
  Default: ``default-test``
* ``geth_reset_chain`` - Boolean for whether the chain should be reset before
  starting the ``geth`` node.  Default ``True``
* ``rpc_host`` - Value to be used for ``--rpcaddr`` default: ``'127.0.0.1'```
* ``rpc_port`` - Value to be used for ``--rpcport`` default: ``'8545'```

.. warning:: This fixture is really slow.  It can take multiple seconds to initialize and cleanup.


``geth_coinbase`` - The coinbase of the running geth node.
----------------------------------------------------------

This is a convenience fixture that returns the coinbase of the testing geth
node.
