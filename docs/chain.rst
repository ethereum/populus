Chain management
================

.. contents:: :local:

Introduction
------------

Populus has the ability to run a variety of blockchains for you, both
programatically and from the command line.



Transient Chains
^^^^^^^^^^^^^^^^

Populus can run two types of transient chains.

* ``testrpc``

    Rusn the ``eth-testrpc`` chain which implements the full JSON-RPC interface
    backed by a test EVM.


* ``temp``

    Runs a blockchain backed by the go-ethereum ``geth`` client.  This chain
    will use a temporary directory for it's chain data which will be cleaned up
    and removed when the chain shuts down.


Local Chains
^^^^^^^^^^^^

Local chains can be setup within your ``populus.ini`` file.  Each local chain
stores its chain data in the ``Project.blockchains_dir`` and persists it's data
between runs.

Local chains are backed by the go-ethereum ``geth`` client.

.. code-block::

    [chain:local]
    # you don't actually have to set any configuration, just create the heading.


Public Chains
^^^^^^^^^^^^^

Populus can run both the main and morden public chains.

* ``mainnet``

    With ``$ populus chain run mainnet`` populus will run the the go-ethereum
    client for you connected to the main public ethereum network.


* ``morden``

    With ``$ populus chain run morden`` populus will run the the go-ethereum
    client for you connected to the testnet public ethereum network.


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

The ``Project.get_chain(chain_name, *chain_args, **chain_kwargs)`` method
returns a ``populus.chain.Chain`` instance that can be used within your code to
run any populus chain.

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


.. code-block:: python

    >>> from populus import Project
    >>> project = Project()
    >>> with project.get_chain('testrpc') as chain:
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
