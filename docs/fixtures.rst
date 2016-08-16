Test fixtures
=============

The following `pytest <http://pytest.org>`__ fixtures are available for your tests.

Populus Config
--------------

* ``populus_config``

This **session** level fixture controls all of the default values for any of
the fixtures that can be configured with either module level variables or
environment variables.

It has the following properties.

* ``rpc_server_port = 8545``
* ``rpc_server_host = '127.0.0.1'``
* ``rpc_client_port = '8545'``
* ``rpc_client_host = '127.0.0.1'``
* ``deploy_client_type = 'ethtester'``
* ``deploy_client_rpc_port = '8545'``
* ``deploy_client_rpc_host = '127.0.0.1'``
* ``deploy_wait_for_block = 0``
* ``deploy_wait_for_block_max_wait = 70``
* ``deploy_address = None``
* ``deploy_max_wait = 70``
* ``deploy_contracts = set()``
* ``deploy_dependencies = {}``
* ``deploy_constructor_args = {}``
* ``deploy_gas_limit = None``
* ``geth_chain_name = 'default-test'``
* ``geth_reset_chain = True``
* ``geth_rpc_port = '8545'``
* ``geth_rpc_host = '127.0.0.1'``
* ``geth_max_wait = 5``
* ``ipc_path = None``

In addition it has the following two special properties that evaluate to the
current working directory of the python process.

* ``geth_project_dir``
* ``project_dir``


Details for what each of these properties configures can be found in their
individual fixture documentation.

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

* ``RPC_CLIENT_HOST``
* ``RPC_CLIENT_PORT``


IPC Client
----------

A python client for the ``JSON-RPC`` server over a unix socket.

* ``ipc_path`` - default is derived from the ``geth_node`` configuration.


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
* set ``deploy_client_type == "ipc"`` in your tests module to use the ipc
  client which interacts with a JSON-RPC server over a socket.

The default value for this is ``ethtester``.

Alternatively, this fixture can be configured by setting the
``DEPLOY_CLIENT_TYPE`` environment variable to the desired string.

To use this fixture configured to use the ``rpc`` client, you must also have a
valid JSON RPC server running.  This can be accomplished by including either of
``rpc_server`` or ``geth_node`` fixtures in your test case.

To use this fixture configured to use the ``ipc`` client, you must also have a
running IPC server which can be done by including the ``geth_node`` fixtures in
your test case.

Deploy Coinbase
---------------

* ``deploy_coinbase``

The address that was used for contract deployment.


Deployed Contracts
------------------

* ``deployed_contracts``

Python object with deployed instances your contracts accessible as properties.

See the ``deploy_client`` fixture for configuration options as to how the
contracts are deployed.

.. note::

    Contract source code is automatically linked against any libraries during
    deployment.  These dependencies are also automatically derived, adding any
    required libraries to the list of contracts to be deployed.


Configuration
^^^^^^^^^^^^^

The following values can be set as either module level variables or as
environment variables in their uppercase form to configure the deployment of
contracts.

* ``deploy_wait_for_block`` Deployment of contracts will not proceed until the
  specified block number has been seen.  Typically, setting this to ``1`` when
  using a ``geth`` based client is a good idea.  (default ``0``)
* ``deploy_wait_for_block_max_wait`` Specifies the maximum amount of time that
  populus will wait for the block number specified by
  ``deploy_wait_for_block``. (default ``70``)
* ``deploy_address`` Specifies the ethereum address that will be used for the
  deployment.  This defaults to the coinbase if unset or falsy.  (default ``None``)
* ``deploy_max_wait`` Specifies the maximum amount of time in seconds that
  populus will wait for the deploying transaction before considering it an
  error. (default ``70``)
* ``deploy_contracts`` If set, only the contracts who's names are contained in
  the value will be deployed. (default ``set()``)
* ``deploy_dependencies`` If any of you contracts must be deployed before
  another, they should be specified with this value.  The keys of the
  dictionary should be the contract which depends on some other(s).  The value
  for each key should be an iterable of the contract names it dependss on.
  (default ``{}``)
* ``deploy_constructor_args`` If any of your contracts need to have arguments
  passed into their constructors, they can be specified with this setting.  The
  keys of this dictionary should be the name for the contract.  The value can
  either be an iterable of constructor args or a callable that takes a single
  argument and returns an iterable of constructor args. The callable will be
  passed a dictionary containing all of the contracts that have alread been
  deployed. (default ``{}``)
* ``deploy_gas_limit`` Specifies the gas value for deploy transactions.  If
  unset or falsy, then a value approximating 90% of the block gas limit will be
  used. (default ``None``)


Geth Node
---------

* ``geth_node``

This is a module level fixture that has a geth node running against the test
chain at ``./chains/default-test/``.

This fixture can be configured by setting the following variables at the top
level of the module in which you are using this fixture.

* ``geth_project_dir`` - The path that should be considered the root of your
  project.  Default: ``os.getcwd()``.
* ``geth_chain_name`` - The name of the test chain that should be used.
  Default: ``default-test``
* ``geth_num_accounts`` - The number of accounts that should be generated for
  the running geth instance.  Default ``1``
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

* ``geth_coinbase``

This is a convenience fixture that returns the coinbase of the testing geth
node.


Geth Accounts
-------------

* ``geth_accounts``

This is a convenience fixture that returns a list of the accounts for the
testing geth node.


Denoms
------

* ``denoms``

Python object with available property access to common denominations
represented as *wei*.

+---------------------+-----------+---------------------------+
| unit                | wei value |                           |
+---------------------+-----------+---------------------------+
| **denoms.babbage**  | 1e3 wei   | 1,000                     |
| **denoms.lovelace** | 1e6 wei   | 1,000,000                 |
| **denoms.shannon**  | 1e9 wei   | 1,000,000,000             |
| **denoms.szabo**    | 1e12 wei  | 1,000,000,000,000         |
| **denoms.finney**   | 1e15 wei  | 1,000,000,000,000,000     |
| **denoms.ether**    | 1e18 wei  | 1,000,000,000,000,000,000 |
+---------------------+-----------+---------------------------+


Accounts
--------

* ``accounts``

Tuple of account addresses available with the current EVM backend.
