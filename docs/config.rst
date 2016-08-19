Configuration
-------------

.. contents:: :local:

Introduction
^^^^^^^^^^^^

Populus supports configuration via a configuration file.  By default, this file
is located at the root of your project and named ``populus.ini``.

In addition to a local project configuration file, populus supports a *global*
configuration file which should be located in your user's ``$HOME`` directory.
Local project configuration will always supercede global configuration.

.. code-block::

    [populus]
    # project level configuration values would be set here.
    default_chain=morden

    [chain:morden]
    default_account=0xd3cda913deb6f67967b99d67acdfa1712c293601

    [chain:local]
    # This makes the `local` chain available.  You don't have to specify any
    # configuration values.


Configuration via CLI
^^^^^^^^^^^^^^^^^^^^^

The configuration file can be easily modified using the following CLI commands.

* ``$ populus config``: Prints the current configuration to the console.
* ``$ populus config:set <option>:<value>``: Sets the ``option`` to the provided
  value under the ``[populus]`` section of the config file.
* ``$ populus config:set --section chain:<chain_name> <option>:<value>``: Sets
  the ``option`` to the provided value under the ``[chain:chain_name]`` section
  of the config file.
* ``$ populus config:unset <option>``: Deletes the ``option`` from the
  ``[populus]`` section of the config file.
* ``$ populus config:unset --section chain:<chain_name> <option>``: Deletes the
  ``option`` from the ``[chain:chain_name]`` section of the config file.


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


Project Level Configuration
---------------------

All project level configuration must be declared under the ``[populus]``
section of the config file.

* ``default_chain``:

  If set, then all command line operations that act on a specific chain will
  default to using this chain.


Chain Level Configuration
-------------------------

Configuration for individual chains should be done under
``[chain:my-chain-name]`` sections.

By default, populus recognizes the following pre-configured chain names.  These
chains do not have to be declared within your configuration file in order to
use them, in which case they will run using a default configuration.

* ``mainnet``: The primary ethereum public main network.
* ``morden``: The primary ethereum public test network.
* ``testrpc``: A test chain backed by the python ``eth-testrpc`` package.  This
  chain does not persist any data between runs.
* ``temp``: A test chain backed by geth that runs in a temporary directory.
  This chain does not persist any data between runs.


Each chain allows configuration via the following options.

* ``default_account``:

    This value should be set to a ``0x`` prefixed address that can be found on
    the given chain.  The ``web3`` object for this chain will have this value
    set to its ``web3.eth.defaultAccount`` value, making it the default sending
    address for all transactions.


* ``deploy_from``:

    This value should be set to a ``0x`` prefixed address that can be found on
    the given chain.  When running ``$ populus deploy`` or ``$ populus
    migrate`` this address will be used as the sending address for all
    transactions.  This value supercedes the ``default_account`` value.


* ``is_external``:

    Indicates that populus will not be responsible for running this chain, and
    will only configure the ``web3`` instance to connect to this chain.  This
    should be used in cases where you want populus to connect to an externally
    running blockchain client.


* ``provider``:

    Specify the python path to the provider class that ``web3.py`` should use
    to connect to this chain.  This should be a dot separated python path such
    as ``web3.providers.ipc.IPCProvider``


* ``ipc_path``:

    When using the ``web3.providers.ipc.IPCProvider`` this value will be used
    to specify the path to the ``geth.ipc`` path.


* ``rpc_host``:

    When using the ``web3.providers.rpc.RPCProvider`` this value will be used
    to specify the host that the provider will connect to.


* ``rpc_port``:

    When using the ``web3.providers.rpc.RPCProvider`` this value will be used
    to specify the port that the provider will connect to.


Here is an example configuration file.


.. code-block::

    [populus]
    default_chain=morden

    [chain:mainnet]
    default_from=0xd3cda913deb6f67967b99d67acdfa1712c293601

    [chain:morden]
    default_account=0x571ce41cde28fb489d269c1b7dd79397bc4abf2a
    provider=web3.providers.rpc.RPCProvider
    rpc_host=http://some.public-testnet-host.net
    rpc_port=8001

    [chain:local_test]
    provider=web3.providers.ipc.IPCProvider
    ipc_path=/some/other/path/geth.ipc
