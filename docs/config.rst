Configuration
=============

.. contents:: :local:

Introduction
------------

Populus is designed to be highly configurable through the project configuration
file.  By default, populus will load the file name ``populus.json`` from the
root of your project.

What you can Configure
^^^^^^^^^^^^^^^^^^^^^^

This config file controls many aspects of populus that are configurable.
Currently the config file controls the following things.

* Compiler settings
* Available chains and how web3 connects to them.



Compiler Configuration
^^^^^^^^^^^^^^^^^^^^^^

The following configuration options are available to control how populus
compiles your project contracts.

.. code-block:: javascript

    {
      "compilation": {
        "contracts_source_dir": "./path/to/contract-source-files",
        "settings": {
          "optimize": true,
          "optimize_runs": 100
        }
      }
    }

Contract Source Directory
"""""""""""""""""""""""""

The directory that project source files can be found in.

* key: ``compilation.contracts_source_dir``
* value: Filesystem path
* default: ``'./contracts'``


Compiler Settings
"""""""""""""""""

Enable or disable compile optimization.

* key: ``compilation.settings.optimize``
* value: Boolean
* default: ``True``


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

* ``populus.chain.EthereumTesterChain``

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

Populus ships with the following *default* configuration 

.. code-block:: javascript 

    {
      'chains': {
        'mainnet': {
          'chain': {'class': 'populus.chain.MainnetChain'},
          'web3': {'$ref': 'web3.GethMainnet'},
        },
        'ropsten': {
          'chain': {'class': 'populus.chain.TestnetChain'},
          'web3': {'$ref': 'web3.GethRopsten'},
        },
        'temp': {
          'chain': {'class': 'populus.chain.TemporaryGethChain'},
          'web3': {'$ref': 'web3.GethEphemeral'},
        },
        'tester': {
          'chain': {'class': 'populus.chain.EthereumTesterChain'},
          'web3': {'$ref': 'web3.Tester'},
        },
        'testrpc': {
          'chain': {'class': 'populus.chain.TestRPCChain'},
          'web3': {'$ref': 'web3.TestRPC'},
        },
      },
      'compilation': {
        'contracts_source_dir': './contracts',
        'settings': {'optimize': True},
      },
      'web3': {
        'GethEphemeral': {
          'provider': {'class': 'web3.providers.ipc.IPCProvider'},
        },
        'GethMainnet': {
          'provider': {
            'class': 'web3.providers.ipc.IPCProvider',
            'settings': {'ipc_path': '/Users/piper/Library/Ethereum/geth.ipc'},
          },
        },
        'GethRopsten': {
          'provider': {
            'class': 'web3.providers.ipc.IPCProvider',
            'settings': {'ipc_path': '/Users/piper/Library/Ethereum/testnet/geth.ipc'},
          },
        },
        'InfuraMainnet': {
          'eth': {'default_account': '0x0000000000000000000000000000000000000001'},
          'provider': {
            'class': 'web3.providers.rpc.HTTPProvider',
            'settings': {'endpoint_uri': 'https://mainnet.infura.io'},
          },
        },
        'InfuraRopsten': {
          'eth': {'default_account': '0x0000000000000000000000000000000000000001'},
          'provider': {
            'class': 'web3.providers.rpc.HTTPProvider',
            'settings': {'endpoint_uri': 'https://ropsten.infura.io'},
          },
        },
        'TestRPC': {
          'provider': {'class': 'web3.providers.tester.TestRPCProvider'},
        },
        'Tester': {
          'provider': {'class': 'web3.providers.tester.EthereumTesterProvider'},
        },
      },
    }


When you author your own ``populus.json`` file populus will automatically merge
the defaults into your declared project configuration. 



Pre-Configured Web3 Connections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following pre-configured configurations are available.  To use one of the
configurations on a chain it should be referenced like this:

.. code-block:: javascript

    {
      "chains": {
        "my-custom-chain": {
            "web3": {"$ref": "web3.GethMainnet"}
        }
      }
    }

GethMainnet
"""""""""""
Web3 connection which will connect to the main ``geth.ipc`` socket.

* key: ``web3.GethMainnet``


GethRopsten
"""""""""""

Web3 connection which will connect to the ropsten ``geth.ipc`` socket.

* key: ``web3.GethRopsten``


GethEphemeral
"""""""""""""

Web3 connection which will connect to a local geth backed chain over the
``geth.ipc`` socket.

* key: ``web3.GethEphemeral``


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
