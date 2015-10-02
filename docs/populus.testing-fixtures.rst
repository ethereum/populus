pytest fixtures provided by Populus
=======================================

The following fixtures are available for your tests.

Populus Config
--------------

* ``populus_config``

This **session** level fixture controls all of the default values for any of
the fixtures that can be configured with either module level variables or
environment variables.

It has the following properties.

* TODO:

EthTester Coinbase
------------------

* ``ethtester_coinbase``

The ``hex`` encoded ``coinbase`` from the ``ethereum.tester`` module
provided by the ``pyethereum`` library.


EthTester Client
----------------

* ``ethtester_client``

A *client* with the same API as the ``rpc_client`` provided by
``eth_rpc_client`` that interacts with the ``ethereum.tester`` module.


Test RPC Server
---------------

Provides a ``JSON-RPC`` server running at ``127.0.0.1:8545``.  This server is
reset at the end of each test run.  The test server is from the ``eth-testrpc``
library and operates on the ``ethereum.tester`` module.

The server can be configured to run on a different host or port by setting the
following variables at the top level of your module.

* ``rpc_server_host`` - default: ``'127.0.0.1'```
* ``rpc_server_port`` - default: ``'8545'```

Alternatively, you can also configure this fixture using the following
environment variables.

* ``RPC_SERVER_HOST``
* ``RPC_SERVER_PORT``


RPC Client
----------

A python client for the ``JSON-RPC`` server.  The hostname and port can be
configuered by setting the following variable at the top level of your python
module.

The client can be configured to connect to a specific port or host by setting
the following variables at the top level of your module.

* ``rpc_client_host`` - default: ``'127.0.0.1'```
* ``rpc_client_port`` - default: ``'8545'```

Alternatively, you can also configure this fixture using the following
environment variables.

* ``RPC_CLINT_HOST``
* ``RPC_CLINT_PORT``


Contracts
---------

* ``contracts``

An object with `~populus.contracts.BaseContract` classes for all of the
compiled contracts in your project.

.. note::

    Note that the contract code used in tests comes from the output from the
    ``compile`` command which means you must recompile your contracts for code
    changes to take effect in your tests.

This fixture can be configured to load contracts from a specified populus
project directory by setting the full path the desired project directy as a top
level module variable named ``project_dir``.  Otherwise, it uses the current
working directory as the project root.


Deploy Client
-------------

* ``deploy_client``

This designates the client that will be used to interface with the ethereum
blockchain to deploy the contracts in the ``deployed_contracts`` fixture.  It
can be configured to use one of two clients.

* set ``deploy_client_type == "ethtester"`` in your tests module to directly
  interface with the ``ethereum.tester`` module.
* set ``deploy_client_type == "rpc"`` in your tests module to use the rpc
  client which interacts with a JSON-RPC server.

The default value for this is ``ethtester``.

Alternatively, this fixture can be configured by setting the
``DEPLOY_CLIENT_TYPE`` environment variable to the desired string.

To use this fixture configured to use the ``rpc`` client, you must also have a
valid JSON RPC server running.  This can be accomplished by including either of
``rpc_server`` or ``geth_node`` fixtures in your test case.


Deployed Contracts
------------------

* ``deployed_contracts``

Python object with deployed instances your contracts accessible as properties.

See the ``deploy_client`` fixture for configuration options as to where the
contracts are deployed.

Configuration
^^^^^^^^^^^^^

TODO


Geth Node
---------

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
* ``geth_rpc_host`` - Value to be used for ``--rpcaddr`` default: ``'127.0.0.1'```
* ``geth_rpc_port`` - Value to be used for ``--rpcport`` default: ``'8545'```

.. warning::

    This fixture is really slow.  It can take multiple seconds to initialize
    and cleanup.  During it's first use, it can also take an extended period of
    time to generate the DAG needed for mining.

Logfiles for the output of the geth node can be found at
``./chains/default-test/logs/``


Geth Coinbase
-------------

This is a convenience fixture that returns the coinbase of the testing geth
node.
