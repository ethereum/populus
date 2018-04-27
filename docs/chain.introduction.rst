.. _chain-introduction:

Introduction to Chains
======================

.. contents:: :local:


Introduction
------------

Populus has the ability to run and/or connect to a variety of blockchains for
you, both programatically and from the command line.


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
    will use a temporary directory for its chain data which will be cleaned up
    and removed when the chain shuts down.


Local Chains
^^^^^^^^^^^^

Local chains can be setup within your ``populus.json`` file.  Each local chain
stores its chain data in the ``populus.Project.blockchains_dir``
and persists its data between runs.

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

.. code-block:: bash

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

The ``populus.Project.get_chain(chain_name, chain_config=None)`` method returns
a ``populus.chain.Chain`` instance that can be used within your code to run any
populus chain. Also read up on the `Web3.py`_ library, which offers additional
functions to communicate with an Ethereum blockchain.

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

.. note:: The ``testrpc`` chain can be run in the same manner.

.. _Web3.py: http://web3py.readthedocs.io/en/latest/
