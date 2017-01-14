Chains
======

.. contents:: :local:

.. py:module:: populus.chain
.. py:currentmodule:: populus.chain


Introduction
------------

Populus has the ability to run a variety of blockchains for you, both
programatically and from the command line.



Transient Chains
^^^^^^^^^^^^^^^^

Populus can run two types of transient chains.

* ``tester``

    A test EVM backed blockchain.


* ``testrpc``

    Runs the ``eth-testrpc`` chain which implements the full JSON-RPC interface
    backed by a test EVM.


* ``temp``

    Runs a blockchain backed by the go-ethereum ``geth`` client.  This chain
    will use a temporary directory for it's chain data which will be cleaned up
    and removed when the chain shuts down.


Local Chains
^^^^^^^^^^^^

Local chains can be setup within your ``populus.json`` file.  Each local chain
stores its chain data in the :py:attribute::`populus.Project.blockchains_dir`
and persists it's data between runs.

Local chains are backed by the go-ethereum ``geth`` client.


Public Chains
^^^^^^^^^^^^^

Populus can run both the main and ropsten public chains.

* ``mainnet``

    With ``$ populus chain run mainnet`` populus will run the the go-ethereum
    client for you connected to the main public ethereum network.


* ``ropsten``

    With ``$ populus chain run ropsten`` populus will run the the go-ethereum
    client for you connected to the ropsten testnet public ethereum network.


Running from the command line
-----------------------------

The ``$ populus chain`` command handles running chains from the command line.

.. code-block::

    $ populus chain
    Usage: populus chain [OPTIONS] COMMAND [ARGS]...

      Manage and run ethereum blockchains.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      reset  Reset a chain removing all chain data and...
      run    Run the named chain.


Running programatically from code
---------------------------------

The :py:method::`populus.Project.get_chain(chain_name, *chain_args,
**chain_kwargs)` method returns a :py:class::`populus.chain.Chain` instance
that can be used within your code to run any populus chain.

Lets look at a basic example of using the ``temp`` chain.

.. code-block:: python

    >>> from populus import Project
    >>> project = Project()
    >>> with project.get_chain('temp') as chain:
    ...     print('coinbase:', chain.web3.eth.coinbase)
    ...
    ...
    coinbase: 0x16e11a86ca5cc6e3e819efee610aa77d78d6e075
    >>>
    >>> with project.get_chain('temp') as chain:
    ...     print('coinbase:', chain.web3.eth.coinbase)
    ...
    ...
    coinbase: 0x64e49c86c5ad1dd047614736a290315d415ef28e


You can see that each time a ``temp`` chain is instantiated it creates a new
data directory and generates new keys.

The ``testrpc`` chain operates in a similar manner in that each time you run
the chain the EVM data is fully reset.  The benefit of the ``testrpc`` server
is that it starts quicker, and has mechanisms for manually resetting the chain.


Here is an example of running the ``tester`` blockchain.


.. code-block:: python

    >>> from populus import Project
    >>> project = Project()
    >>> with project.get_chain('tester') as chain:
    ...     print('coinbase:', chain.web3.eth.coinbase)
    ...     print('blockNumber:', chain.web3.eth.blockNumber)
    ...     chain.mine()
    ...     print('blockNumber:', chain.web3.eth.blockNumber)
    ...     snapshot_id = chain.snapshot()
    ...     print('Snapshot:', snapshot_id)
    ...     chain.mine()
    ...     chain.mine()
    ...     print('blockNumber:', chain.web3.eth.blockNumber)
    ...     chain.revert(snapshot_id)
    ...     print('blockNumber:', chain.web3.eth.blockNumber)
    ...
    coinbase: 0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1
    blockNumber: 1
    blockNumber: 2
    Snapshot: 0
    blockNumber: 4
    blockNumber: 2

The ``testrpc`` chain can be run in the same manner.

Here is an example how to have your own py.test fixture for launching
a temporary Geth instance with a fresh blockchain.

See

* :py:meth:`populus.project.Project.get_chain`

* :py:class:`populus.project.Project`

* :py:class:`populus.chain.TemporaryGethChain`

* :py:class:`populus.config.Config`

* :py:class:`web3.Web3`

Example:

.. code-block:: python

    import os

    from populus.project import Project
    from populus.utils.config import Config
    from web3 import Web3
    from web3 import RPCProvider


    @pytest.yield_fixture(scope="session")
    def web3() -> Web3:
        """A py.test fixture to get a Web3 interface to a temporary geth instance.

        This is session scoped fixture.
        Geth is launched only once during the beginning of the test run.

        Geth will have a huge premined instant balance on its coinbase account.
        Geth will also mine our transactions on artificially low difficulty level.

        :yield: :py:class:`web3.Web3` instance
        """

        project = Project()

        # Project is configured using populus.config.Config class
        # which is a subclass of Python config parser.
        # Instead of reading .ini file, here we dynamically
        # construct the configuration.
        project.config = Config()

        # Settings come for [populus] section of the config.
        project.config.add_section("populus")

        # Configure where Populus can find our contracts.json
        build_dir = os.path.join(os.getcwd(), "websauna", "wallet", "ethereum")
        project.config.set("populus", "build_dir", build_dir)

        chain_kwargs = {

            # Force RPC provider instead of default IPC one
            "provider": RPCProvider,

            # Adjust geth verbosity for less
            # output so that test failures are easier to read.
            "verbosity": "2"
        }

        # This returns TemporaryGethChain instance as geth_proc
        with project.get_chain("temp", **chain_kwargs) as geth_proc:

            web3 = geth_proc.web3

            # Allow access to sendTransaction() to use coinbase balance
            # to deploy contracts. Password is from py-geth
            # default_blockchain_password file. Assume we don't
            # run tests for more than 9999 seconds
            coinbase = web3.eth.coinbase
            success = web3.personal.unlockAccount(
                coinbase,
                passphrase="this-is-not-a-secure-password",
                duration=9999)

            assert success, "Could not unlock test geth coinbase account"

            yield web3


Access To Contracts
-------------------

.. py:class:: Chain

All chain objects present the following API for interacting with your project
contracts.

.. py:method:: Chain.get_contract_factory(contract_name, link_dependencies=None, validate_bytecode=True)

    Returns the contract factory for the contract indicated by
    ``contract_name`` from the chain's ``compiled_contracts``.

    If provided, ``link_dependencies`` should be a dictionary that maps library
    names to their on chain addresses that will be used during bytecode
    linking.

    If truthy (the default), ``validate_bytecode`` indicates whether the
    bytecode for any library dependencies for the given contract should be
    validated to match the on chain bytecode.

    If your project has no project migrations then the data used for these
    contract factories will come directly from the compiled project contracts.

    If your project has migrations then the data used to build your contract
    factories will be populutated as follows.:

        #. The newest migration that has been run which deploys the requested
           contract.
        #. The newest migration which contains this contract in it's
           ``compiled_contracts`` property
        #. The compiled project contracts.


.. py:method:: Chain.get_contract(contract_name, link_dependencies=None, validate_bytecode=True)

    Returns the contract instance indicated by the ``contract_name`` from the
    chain's ``compiled_contracts``.

    The ``link_dependencies`` argument behaves the same was as specified in the
    ``get_contract_factory`` method.

    The ``validate_bytecode`` argument behaves the same way as specified in the
    ``get_contract_factory`` with the added condition that the bytecode for the
    requested contract will also be checked.

    .. note::
        
        When using a ``TestRPCChain`` the ``get_contract`` method will lazily
        deploy your contracts for you.  This lazy deployment will only work for
        simple contracts which do not require constructor arguments.


.. py:method:: Chain.is_contract_available(contract_name, link_dependencies=None, validate_bytecode=True, raise_on_error=False)

    Returns ``True`` or ``False`` as to whether the contract indicated by
    ``contract_name`` from the chain's ``compiled_contracts`` is available
    through the ``Chain.get_contract`` API.

    The ``link_dependencies`` argument behaves the same was as specified in the
    ``get_contract_factory`` method.

    The ``validate_bytecode`` argument behaves the same way as specified in the
    ``get_contract_factory`` with the added condition that the bytecode for the
    requested contract will also be checked.

    If ``raise_on_error`` is truthy, then the method will raise an exception
    instead of returning ``False`` for any of the failure cases.


Waiting for Things
------------------

Each chain object exposes the following API through a property ``chain.wait``.
The ``timeout`` parameter determines how long this will block before raising a
``gevent.Timeout`` exception.  The ``poll_interval`` determines how long it
should wait between polling.  If ``poll_interval == None`` then
``random.random()`` will be used to determine the poling interval.


.. py:method:: Chain.wait.for_contract_address(txn_hash, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds returning the contract address from the
    transaction receipt for the given ``txn_hash``.


.. py:method:: Chain.wait.for_receipt(txn_hash, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds returning the transaction receipt for
    the given ``txn_hash``.


.. py:method:: Chain.wait.for_block(block_number=1, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds waiting until the highest block on the
    current chain is at least ``block_number``.


.. py:method:: Chain.wait.for_unlock(account=web3.eth.coinbase, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds waiting until the account specified by
    ``account`` is unlocked.  If ``account`` is not provided,
    ``web3.eth.coinbase`` will be used.


.. py:method:: Chain.wait.for_peers(peer_count=1, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds waiting for the client to have at
    least ``peer_count`` peer connections.


.. py:method:: Chain.wait.for_syncing(timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds waiting the chain to begin syncing.
