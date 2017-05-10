Release Notes
=============

.. _v1.7.0-release-notes:

1.7.0
-----

- Remove deprecated ``chain.contract_factories`` API.
- Remove deprecated ``chain.get_contract_factory`` API.
- Remove deprecated ``chain.is_contract_available`` API.
- Remove deprecated ``chain.get_contract`` API.
- Remove deprecated ``chain.deployed_contracts`` API.
- Remove deprecated ``contracts`` pytest fixture.
- Remove deprecated ``project.compiled_contracts_file_path`` API
- Remove deprecated ``project.contracts_dir`` API
- Remove deprecated ``project.build_dir`` API
- Remove deprecated ``project.compiled_contracts`` API
- Remove deprecated ``project.blockchains_dir`` API
- Remove deprecated ``project.get_blockahin_data_dir`` API
- Remove deprecated ``project.get_blockchain_chaindata_dir`` API
- Remove deprecated ``project.get_blockchain_dapp_dir`` API
- Remove deprecated ``project.get_blockchain_ipc_path`` API
- Remove deprecated ``project.get_blockchain_nodekey_path`` API

.. _v1.6.9-release-notes:

1.6.9
-----

- Bump py-geth version to account for removed ``--ipcapi`` CLI flag.


.. _v1.6.8-release-notes:

1.6.8
-----

- Allow for empty passwords when unlocking accounts.


.. _v1.6.7-release-notes:

1.6.7
-----

- Bugfix for registrar address sorting to handle nodes which were fast synced
  and do not have access to the full chain history.


.. _v1.6.6-release-notes:

1.6.6
-----

- Add support to contract provider to handle case where registrar has more than
  one address for a given contract.


.. _v1.6.5-release-notes:

1.6.5
-----

- Bugfix for compilation of abstract contracts.


.. _v1.6.4-release-notes:

1.6.4
-----

- Bugfix for ``project.config`` setter function not setting correct value.


.. _v1.6.3-release-notes:

1.6.3
-----

- Add ``TestContractsBackend`` for loading test contracts.


.. _v1.6.2-release-notes:

1.6.2
-----

- Fix incorrect example test file from ``$ populus init`` command.


.. _v1.6.1-release-notes:

1.6.1
-----

- Fix warning message for outdated config file so that it actually shows up in terminal.

.. _v1.6.0-release-notes:

1.6.0
-----

- Introduce new :ref:`Registrar API <chain-registrar>`.
- Introduce new :ref:`Provider API <chain-provider>`.
- Deprecate ``Chain.get_contract_factory``, ``Chain.get_contract`` and ``Chain.is_contract_available`` APIs.
- Deprecate ``Chain.contract_factories`` API.
- Deprecate ``Chain.deployed_contracts`` API.
- Remove deprecated migrations API.


1.5.3
-----

- Bump ``web3.py`` version to pull in upstream fixes for ``ethereum-abi-utils``


1.5.2
-----

- Bugfix for remaining ``web3.utils`` imports


1.5.1
-----

- Update upstream ``web3.py`` dependency.
- Switch to use ``ethereum-utils`` library.

1.5.0
-----

- Remove gevent dependency
- Mark migrations API for deprecation.
- Mark unmigrated_chain testing fixture for deprecation.
- Mark ``contracts`` fixture for deprecation.  Replaced by ``base_contract_factories`` fixture.
- Deprecate and remove old ``populus.ini`` configuration scheme.
- Add new configuration API.

1.4.2
-----

- Upstream version bumps for web3 and ethtestrpc
- Change to use new web3.providers.tester.EthereumTesterProvider for test fixtures.

1.4.1
-----

- Stop-gap fix for race-condition error from upstream: https://github.com/pipermerriam/web3.py/issues/80

1.4.0
-----

- Contract source directory now configurable via populus.ini file.
- Updates to upstream dependencies.

1.3.0
-----

- Bugfix for geth data_dir directory on linux systems.

1.2.2
-----

- Support solc 0.4.x

1.2.1
-----

- Support legacy JSON-RPC spec for ``eth_getTransactionReceipt`` in wait API.

1.2.0
-----

- All function in the ``chain.wait`` api now take a ``poll_interval`` parameter
  which controls how aggressively they will poll for changes.
- The ``project`` fixture now caches the compiled contracts across test runs.

1.1.0
-----

This release begins the first deprecation cycle for APIs which will be removed
in future releases.

- Deprecated: Entire migrations API
- New configuration API which replaces the ``populus.ini`` based configuration.
- Removal of ``gevent`` as a required dependency.  Threading and other
  asynchronous operations now default to standard library tools with the option
  to enable the gevent with an environment variable
  ``THREADING_BACKEND==gevent``


1.0.0
-----

This is the first release of populus that should be considered stable.

- Remove ``$ populus web`` command
- Remove ``populus.solidity`` module in favor of ``py-solc`` package for
  solidity compilation.
- Remove ``populus.geth`` module in favor of ``py-geth`` for running geth.
- Complete refactor of pytest fixtures.
- Switch to ``web3.py`` for all blockchain interactions.
- Compilation:
  - Remove filtering.  Compilation now always compiles all contracts.
  - Compilation now runs with optimization turned on by default.  Can be disabled with ``--no-optimizie``.
  - Remove use of  ``./project-dir/libraries`` directory.  All contracts are now expected to reside in the ``./project-dir/contracts`` directory.
- New ``populus.Project`` API.
- New Migrations API:
  - ``$ populus chain init`` for initializing a chain with the Registrar contract.
  - ``$ populus makemigration`` for creating migration files.
  - ``$ populus migrate`` for executing migrations.
- New configuration API:
  - New commands ``$ populus config``, ``$ populus config:set`` and ``$ populus config:unset`` for managing configuratino.
- New Chain API:
  - Simple programatic running of project chains.
  - Access to ``web3.eth.contract`` objects for all project contracts.
  - Access to pre-linked code based on previously deployed contracts.

0.8.0
-----

- Removal of the ``--logfile`` command line argument.  This is a breaking change
  as it will break when used with older installs of ``geth``.

0.7.5
-----

- Bugfix: ``populus init`` now creates the ``libraries`` directory
- Bugfix: ``populus compile --watch`` no longer fails if the ``libraries``
  directory isn't present.

0.7.4
-----

- Bugfix for the ``geth_accounts`` fixture.
- Bugfix for project initialization fixtures.
- Allow returning of ``indexed`` event data from Event.get_log_data
- Fix EthTesterClient handling of TransactionErrors to allow continued EVM
  interactions.
- Bugfix for long Unix socket paths.
- Enable whisper when running a geth instance.
- Better error output from compile errors.
- Testing bugfixes.

0.7.3
-----

- Add ``denoms`` pytest fixture
- Add ``accounts`` pytest fixture
- Experimental synchronous function calls on contracts with ``function.s(...)``
- Bugfixes for function group argument validation.
- Bugfixes for error handling within EthTesterClient
- Inclusion of Binary Runtime in compilation
- Fixes for tests that were dependent on specific solidity versions.

0.7.2
-----

- Make the ethtester client work with asynchronous code.

0.7.1
-----

- Adds ``ipc_client`` fixture.

0.7.0
-----

- When a contract function call that is supposed to return data returns no data
  an error was thown.  Now a custom exception is thrown.  This is a breaking
  change as previously for addresses this would return the empty address.

0.6.6
-----

- Actually fix the address bug.

0.6.5
-----

- Fix bug where addresses were getting double prefixed with ``0x``

0.6.3
-----

- Bugfix for Event.get_log_data
- Add ``get_code`` and ``get_accounts`` methods to EthTesterClient
- Add ``0x`` prefixing to addresses returned by functions with multiple return
  values.

0.6.3
-----

- Shorted path to cli tests to stay under 108 character limit for unix sockets.
- Adds tracking of contract addresses deployed to test chains.
- New ``redeploy`` feature available within ``populus attach`` as well as
  notification that your contracts have changed and may require redeployment.

0.6.2
-----

- Shorted path to cli tests to stay under 108 character limit for unix sockets.
- Allow passing ``--verbosity`` tag into ``populus chain run``
- Expand documentation with example use case for populus deploy/chain/attach
  commands.

0.6.1
-----

- Change the *default* gas for transactions to be a percentage of the max gas.

0.6.0
-----

- Improve ``populus deploy`` command.
        - Optional dry run to test chain
        - Prompts user for confirmation on production deployments.
        - Derives gas needs based on dry-run deployment.
- Addition of ``deploy_coinbase`` testing fixture.
- Renamed ``Contract._meta.rpc_client`` to be ``Contract._meta.blockchain_client``
  to be more appropriately named since the ``EthTesterClient`` is not an RPC
  client.
- Renamed ``rpc_client`` argument to ``blockchain_client`` in all relevant functions.
- Moved ``get_max_gas`` function onto blockchain clients.
- Moved ``wait_for_transaction`` function onto blockchain clients.
- Moved ``wait_for_block`` function onto blockchain clients.
- Bugfix when decoding large integers.
- Reduced ``gasLimit`` on genesis block for test chains to ``3141592``.
- Updated dependencies to newer versions.

0.5.4
-----

- Additional support for *library* contracts which will be included in
  compilation.
- ``deployed_contracts`` automatically derives deployment order and dependencies
  as well as linking library addresses.
- ``deployed_contracts`` now comes with the transaction receipts for the
  deploying transaction attached.
- Change to use ``pyethash`` from pypi


0.5.3
-----

- New ``populus attach`` command for launching interactive python repl with
  contracts and rpc client loaded into local scope.
- Support for auto-linking of library contracts for the ``deployed_contracts``
  testing fixture.


0.5.2
-----

- Rename ``rpc_server`` fixture to ``testrpc_server``
- Introduce ``populus_config`` module level fixture which holds all of the
  default values for other populus module level fixtures that are configurable.
- Add new configuration options for ``deployed_contracts`` fixture to allow
  declaration of which contracts are deployed, dependency ordering and
  constructor args.
- Improve overall documentation around fixtures.

0.5.1
-----

- Introduce the ``ethtester_client`` which has the same API as the
  eth_rpc_client.Client class but interacts directly with the ``ethereum.tester``
  module
- Add ability to control the manner through which the ``deployed_contracts``
  fixture communicates with the blockchain via the ``deploy_client`` fixture.
- Re-organization of the contracts module.
- Support for multiple contract functions with the same name.
- Basic support for extracting logs and log data from transactions.

0.5.0
-----

- Significant refactor to the ``Contract`` and related ``Function`` and ``Event``
  objects used to interact with contracts.
- Major improvements to robustness of ``geth_node`` fixture.
- ``deployed_contracts`` testing fixture no longer provides it's own rpc server.
  Now you must either provide you own, or use the ``geth_node`` or ``rpc_server``
  alongside it in tests.
- ``geth_node`` fixture now writes to a logfile located in
  ``./chains/<chain-name>/logs/`` for both cli and test case runs.

0.4.3
-----

- Add support for address function args with a 0x prefix.

0.4.2
-----

- Add ``init`` command for initializing a populus project.

0.4.1
-----

- Missing ``index.html`` file.

0.4.0
-----

- Add blockchain management via ``populus chain`` commands which wraps ``geth`` library.
    - ``populus chain run <name>`` for running the chain
    - ``populus chain reset <name>`` for resetting a chain
- Add html/css/js development support.
    - Development webserver via ``populus web runserver``
    - Conversion of compiled contracts to web3 contract objects in javascript.

0.3.7
-----

- Add support for decoding multiple values from a solidity function call.

0.3.6
-----

- Add support for decoding ``address```` return types from contract functions.

0.3.5
-----

- Add support for contract constructors which take arguments via the new
  ``constructor_args`` parameter to the ``Contract.deploy`` method.

0.3.4
-----

- Fix bug where null bytes were excluded from the returned bytes.

0.3.3
-----

- Fix a bug in the ``sendTransaction`` methods for contract functions that did
  not pass along most of the ``**kwargs``.
- Add new ``Contract.get_balance()`` method to contracts.

0.3.2
-----

- Enable decoding of ``bytes`` types returned by contract function calls.

0.3.1
-----

- Enable decoding of ``boolean`` values returned by contract function calls.

0.3.0
-----

- Removed ``watch`` command in favor of passing ``--watch`` into the ``compile``
  command.
- Add granular control to the ``compile`` command so that you can specify
  specific files, contract names, or a combination of the two.

0.2.0
-----

- Update to ``pypi`` version of ``eth-testrpc``
- Add new watch command which observes the project contracts and recompiles
  them when they change.
- Improved shell output for compile command.
- Re-organized portions of the ``utils`` module into a new ``compilation`` module.

0.1.4
-----

- Fix broken import in ``cli`` module.

0.1.3
-----

- Remove the local RPC client in favor of using
  https://github.com/pipermerriam/ethereum-rpc-client

0.1.2
-----

- Add missing pytest dependency.

0.1.1
-----

- Fix bug when deploying contracts onto a real blockchain.

0.1.0
-----

- Project Creation
