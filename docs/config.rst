Configuration
=============

.. contents:: :local:

Introduction
------------

Populus is designed to be highly configurable through the project configuration
file.  By default, populus will load the file name ``populus.json`` from the
root of your project.

The ``$ populus init`` command will write the full default configuration.


What you can Configure
^^^^^^^^^^^^^^^^^^^^^^

This config file controls many aspects of populus that are configurable.
Currently the config file controls the following things.

* Project root directory
* Contract source file location
* Compiler settings
* Available chains and how web3 connects to them.


Compiler Configuration
^^^^^^^^^^^^^^^^^^^^^^

The following configuration options are available to control how populus
compiles your project contracts.

.. code-block:: javascript

    {
      "compilation": {
        "contracts_dir": "./path/to/contract-source-files",
        "settings": {
          "optimize": true,
          "optimize_runs": 100
        }
      }
    }

Contract Source Directory
"""""""""""""""""""""""""

The directory that project source files can be found in.

* key: ``compilation.contracts_dir``
* value: Filesystem path
* default: ``'./contracts'``


Compiler Settings
"""""""""""""""""

Enable or disable compile optimization.

* key: ``compilation.settings.optimize``
* value: Boolean
* default: ``True``

Determine compiler output.

* key: ``compilation.settings.output_values``
* value: List of strings
* default: ``['bin', 'bin-runtime', 'abi']``

Set `solc import path remappings <https://github.com/pipermerriam/py-solc#import-path-remappings>_`. This is especially useful if you want to use libraries like `OpenZeppelin <https://github.com/OpenZeppelin/zeppelin-solidity/>`_ with your project. Then you can directly import Zeppelin contracts like ``import "zeppelin/contracts/token/TransferableToken.sol";``.

* key: ``compilation.settings.import_remapping``
* value: String
* default: ``None``
* example: ``zeppelin=zeppelin`` (assuming you have done ``git submodule add git@github.com:OpenZeppelin/zeppelin-solidity.git zeppelin``in your project root)

Chains
^^^^^^

The ``chains`` key within the configuration file declares what chains populus
has access to and how to connect to them.  Populus comes pre-configured with
the following chains.

* ``'mainnet'``: Connects to the public ethereum mainnet via ``geth``.
* ``'ropsten'``: Connects to the public ethereum ropsten testnet via ``geth``.
* ``'tester'``: Uses an ephemeral in-memory chain backed by pyethereum.
* ``'testrpc'``: Uses an ephemeral in-memory chain backed by pyethereum.
* ``'temp'``: Local private chain whos data directory is removed when the chain
  is shutdown.  Runs via ``geth``.

.. code-block:: javascript

    {
      "chains": {
        "my-chain": {
          ... // The chain settings.
        }
      }
    }


Individual Chain Settings
^^^^^^^^^^^^^^^^^^^^^^^^^

Each key and value in the ``chains`` portion of the configuration corresponds
to the name of the chain and the settings for that chain.  Each chain has two
primary sections, ``web3`` and ``chain`` configuration settings.

.. code-block:: javascript

    {
      "chains": {
        "my-chain": {
          "chain": {
            "class": "populus.chain.LocalGethChain"
          },
          "web3": {
            "provider": {
              "class": "web3.providers.ipc.IPCProvider"
            }
          }
        }
      }
    }

The above chain configuration sets up a new local private chain within your
project.  The chain above would set it's data directory to
``<project-dir>/chains/my-chain/``.

To simplify configuration of chains you can use the ``ChainConfig`` object.

.. code-block:: python

    >>> from populus.config import ChainConfig
    >>> chain_config = ChainConfig()
    >>> chain_config.set_chain_class('local')
    >>> chain_config['web3'] = web3_config  # see below for the Web3Config object
    >>> project.config['chains.my-chain'] = chain_config

The ``set_chain_class()`` method can take any of the following values.

- These strings
    - ``chain_config.set_chain_class('local') => 'populus.chain.LocalGethChain'``
    - ``chain_config.set_chain_class('external') => 'populus.chain.ExternalChain'``
    - ``chain_config.set_chain_class('tester') => 'populus.chain.TesterChain'``
    - ``chain_config.set_chain_class('testrpc') => 'populus.chain.TestRPCChain'``
    - ``chain_config.set_chain_class('temp') => 'populus.chain.TemporaryGethChain'``
    - ``chain_config.set_chain_class('mainnet') => 'populus.chain.MainnetChain'``
    - ``chain_config.set_chain_class('testnet') => 'populus.chain.TestnetChain'``
    - ``chain_config.set_chain_class('ropsten') => 'populus.chain.TestnetChain'``
- Full python paths to the desired chain class.
    - ``chain_config.set_chain_class('populus.chain.LocalGethChain') => 'populus.chain.LocalGethChain'``
    - ``chain_config.set_chain_class('populus.chain.ExternalChain') => 'populus.chain.ExternalChain'``
    - ``...``
- The actual chain class.
    - ``chain_config.set_chain_class(LocalGethChain) => 'populus.chain.LocalGethChain'``
    - ``chain_config.set_chain_class(ExternalChain) => 'populus.chain.ExternalChain'``
    - ``...``


Chain Class Settings
""""""""""""""""""""

Determines which chain class will be used for the chain.

* key: ``chains.<chain-name>.chain.class``
* value: Dot separated python path to the chain class that should be used.
* required: Yes

Available options are:

* ``populus.chain.ExternalChain``

    A chain that populus does not manage or run.  This is the correct class to
    use when connecting to a node that is already running.

* ``populus.chain.TestRPCChain``

    An ephemeral chain that uses the python ``eth-testrpc`` package to run an
    in-memory ethereum blockchain.  This chain will spin up an HTTP based RPC
    server.

* ``populus.chain.TesterChain``

    An ephemeral chain that uses the python ``eth-testrpc`` package to run an
    in-memory ethereum blockchain.  This chain **must** be used in conjunction
    with a web configuration using the provider ``EthereumTesterProvider``.

* ``populus.chain.LocalGethChain``

    A geth backed chain which will setup it's own data directory in the
    ``./chains`` directory in the root of your project.

* ``populus.chain.TemporaryGethChain``

    An ephemeral chain backed by ``geth`` which uses a temporary directory as
    the data directory which is removed when the chain is shutdown.

* ``populus.chain.TestnetChain``

    A ``geth`` backed chain which connects to the public Ropsten test network.

* ``populus.chain.MainnetChain``

    A ``geth`` backed chain which connects to the main public network.



Web3
""""

Configuration for the Web3 instance that will be used with this chain.  See
*Web3 Configuration* for more details.

* key: ``chains.<chain-name>.web3``
* value: Web3 Configuration
* required: Yes


Web3 Configuration
------------------

Configuration for setting up a Web3 instance.

.. code-block:: javascript

    {
      "provider": {
        "class": "web3.providers.ipc.IPCProvider",
        "settings": {
          "ipc_path": "/path/to/geth.ipc"
        }
      }
      "eth": {
        "default_account": "0xd3cda913deb6f67967b99d67acdfa1712c293601",
      }
    }

In order to simplify configuring Web3 instances you can use the ``Web3Config``
class.

.. code-block:: python

    >>> from populus.config import Web3Config
    >>> web3_config = Web3Config()
    >>> web3_config.set_provider('ipc')
    >>> web3_config.provider_kwargs['ipc_path'] = '/path/to/geth.ipc'
    >>> web3.config.default_account = '0x0000000000000000000000000000000000000001'
    >>> project.config['chains.my-chain.web3'] = web3_config
    >>> project.write_config()  # optionally persist the configuration to disk


Provider Class
^^^^^^^^^^^^^^

Specifies the import path for the provider class that should be used.

* key: ``provider.class``
* value: Dot separated python path
* required: Yes

Provider Settings
^^^^^^^^^^^^^^^^^

Specifies the ``**kwargs`` that should be used when instantiating the provider.

* key: ``provider.settings``
* value: Key/Value mapping


Default Account
^^^^^^^^^^^^^^^

If present the ``web3.eth.defaultAccount`` will be populated with this address.

* key: ``eth.default_account``
* value: Ethereum Address


Configuration API
-----------------

The project configuration can be accessed as a property on the ``Project``
object via ``project.config``.  This object is a dictionary-like object with
some added convenience APIs.

Project configuration is represented as a nested key/value mapping.

Getting and Setting
^^^^^^^^^^^^^^^^^^^

The ``project.config`` object exposes the following API for getting and setting
configuration values.  Supposing that the project configuration file contained
the following data.

.. code-block:: javascript

    {
      'a': {
        'b': {
          'c': 'd',
          'e': 'f'
        }
      },
      'g': {
        'h': {
          'i': 'j',
          'k': 'l'
        }
      }
    }


The config object supports retrieval of values in much the same manner as a
dictionary.  For convenience, you can also access *deep* nested values using a
single key which is dot-separated combination of all keys.


.. code-block:: python

    >>> project.config.get('a')
    {
      'b': {
        'c': 'd',
        'e': 'f'
      }
    }
    >>> project.config['a']
    {
      'b': {
        'c': 'd',
        'e': 'f'
      }
    }
    >>> project.config.get('a.b')
    {
      'c': 'd',
      'e': 'f'
    }
    >>> project.config['a.b']
    {
      'c': 'd',
      'e': 'f'
    }
    >>> project.config.get('a.b.c')
    'd'
    >>> project.config['a.b.c']
    'd'
    >>> project.config.get('a.b.x')
    None
    >>> project.config['a.b.x']
    KeyError: 'x'
    >>> project.config.get('a.b.x', 'some-default')
    'some-default'

The config object also supports setting of values in the same manner.

.. code-block:: python

    >>> project.config['m'] = 'n'
    >>> project.config
    {
      'a': {
        'b': {
          'c': 'd',
          'e': 'f'
        }
      },
      'g': {
        'h': {
          'i': 'j',
          'k': 'l'
        }
      },
      'm': 'n'
    }
    >>> project.config['o.p'] = 'q'
    >>> project.config
    {
      'a': {
        'b': {
          'c': 'd',
          'e': 'f'
        }
      },
      'g': {
        'h': {
          'i': 'j',
          'k': 'l'
        }
      },
      'm': 'n'
      'o': {
        'p': 'q'
      }
    }

Config objects support existence queries as well.

.. code-block:: python

    >>> 'a' in project.config
    True
    >>> 'a.b' in project.config
    True
    >>> 'a.b.c' in project.config
    True
    >>> 'a.b.x' in project.config
    False


Config References
^^^^^^^^^^^^^^^^^

Sometimes it is useful to be able to re-use some configuration in multiple
locations in your configuration file.  This is where references can be useful.
To reference another part of your configuration use an object with a single key
of ``$ref``.  The value should be the full key path that should be used in
place of the reference object.

.. code-block:: javascript

    {
      'a': {
        '$ref': 'b.c'
      }
      'b': {
        'c': 'd'
      }
    }

In the above, the key ``a`` is a reference to the value found under key ``b.c``

.. code-block:: python

    >>> project.config['a']
    ['d']
    >>> project.config.get('a')
    ['d']



Defaults
--------

Populus ships with many defaults which can be overridden as you see fit.


Built-in defaults
^^^^^^^^^^^^^^^^^

Populus ships with the following *default* configuration.  

.. literalinclude:: ../populus/assets/defaults.config.json
   :language: javascript


It is recommended to use the ``$ populus init`` command to populate this file
as it contains useful defaults.


Pre-Configured Web3 Connections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following pre-configured configurations are available.  To use one of the
configurations on a chain it should be referenced like this:

.. code-block:: javascript

    {
      "chains": {
        "my-custom-chain": {
            "web3": {"$ref": "web3.GethIPC"}
        }
      }
    }

GethIPC
"""""""
Web3 connection which will connect to geth using an IPC socket.

* key: ``web3.GethIPC``


InfuraMainnet
"""""""""""""

Web3 connection which will connect to the mainnet ethereum network via Infura.

* key: ``web3.InfuraMainnet``


InfuraRopsten
"""""""""""""

Web3 connection which will connect to the ropsten ethereum network via Infura.

* key: ``web3.InfuraRopsten``


TestRPC
"""""""

Web3 connection which will use the ``TestRPCProvider``.

* key: ``web3.TestRPC``


Tester
""""""

Web3 connection which will use the ``EthereumTesterProvider``.

* key: ``web3.Tester``


Command Line Interface
----------------------

You can manage your configuration using the command line with the ``$ populus
config`` command.

.. code-block:: bash

    $ populus config
    Usage: populus config [OPTIONS] COMMAND [ARGS]...

      Manage and run ethereum blockchains.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      delete  Deletes the provided key/value pairs from the...
      get     Gets the provided key/value pairs from the...
      list    Prints the project configuration out to the...
      set     Sets the provided key/value pairs in the...

To interact with nested keys simply separate them with a ``.``.


.. code-block:: bash

    $ populus config list
    some.nested.key_a: the_value_a
    some.nested.key_b: the_value_b
    $ populus config set some.nested.key_c:the_value_c
    $ populus config list
    some.nested.key_a: the_value_a
    some.nested.key_b: the_value_b
    some.nested.key_c: the_value_c
    $ populus config get some.nested.key_a
    some.nested.key_a: the_value_a
    $ populus config delete some.nested.key_a
    some.nested.key_a: the_value_a (deleted)
