Configuration
-------------

.. contents:: :local:

Introduction
^^^^^^^^^^^^

Populus supports configuration via a configuration file.  By default, populus
will search the following paths for a file named ``populus.ini``

* ``/the-path-to/your-project-directory/populus.ini``
* ``$HOME/populus.ini``

A simple populus config file will look something like the following.


.. code-block::

    [populus]
    default_chain=morden

    [chain:morden]
    provider=web3.providers.rpc.RPCProvider
    port=8001


This filed declares that when connecting to the morden test network populus
should use the RPC provider (instead of the default IPC based provider), and
that it should connect over port ``8001`` instead of the default ``8545``.


Setting and Unsetting
^^^^^^^^^^^^^^^^^^^^^

The configuration file can be easily modified using the ``$ populus config``
command.


.. code-block::

    $ populus config:set default_chain:mainnet
    $ populus config:set project_dir:some/sub-directory
    $ populus config
    [populus]
      default_chain = mainnet
      project_dir = some/sub-dir

    $ populus config:set --section chain:mainnet provider:web3.providers.rpc.RPCProvider
    $ populus config:set --section chain:mainnet port:8001
    $ populus config
    [populus]
      default_chain = mainnet
      project_dir = some/sub-dir

    [chain:mainnet]
      provider = web3.providers.rpc.RPCProvider
      port = 8001

    $ populus config:unset project_dir
    $ populus config
    [populus]
      default_chain = mainnet

    [chain:mainnet]
      provider = web3.providers.rpc.RPCProvider
      port = 8001

    $ populus config:unset --section chain:mainnet *
    Are you sure you want to remove the entire 'chain:mainnet' section? [Y/n] Y
    $ populus config
    [populus]
      default_chain = mainnet


Configuration Options
^^^^^^^^^^^^^^^^^^^^^

The following configuration options are recognized by populus.


Project Configuration
---------------------

All project level configuration should happen under the ``[populus]`` section
of the config file.

* ``TODO``


Chain Configuration
-------------------

Configuration for individual chains should be done under
``[chain:my-chain-name]`` sections.

By default, populus recognizes the following pre-configured chain names.

* ``mainnet``: The primary public ethereum network.
* ``morden``: The ethereum test network.
* ``testrpc``: A test chain backed by the ``eth-testrpc`` package.  *(Does not
  persist any data between runs)*
* ``temp``: A test chain backed by geth that runs in a temporary directory
  which is removed when the chain shuts down.

Each chain allows configuration via the following options.

* ``provider``

Specify the python path to the provider class that ``web3.py`` should use to
connect to this chain.
