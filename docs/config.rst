Configuration
=============

.. contents:: :local:

Introduction
------------

Populus is designed to be highly configurable through the configuration
files.

By default, populus will load the configuration from two files: the user-scope main config file
at ``~/.populus/config.json``, and the project-scope config file, at the project directory,
``project.json``.

Both files share the same JSON schema. You should use the ``project.json`` file for local changes that
apply to specific project,
and the user-scope file for the environment configs, which apply to all your projects.

When a configuration key exists in both the user-config and the project-config, the project-config overrides the user-config.
However, programmatically you have access to both configs and can decide in runtime to choose otherwise.

The ``$ populus init`` command writes a minimal ``project.json`` default file to the project directory.

.. note::

  The ``project.json`` file is required, and all the populus commands require a directory with a project config file.

A Note for Django users
^^^^^^^^^^^^^^^^^^^^^^^

If you are used to django's ``settings.py`` file, populus is quite different.
The configuration is saved in JSON files, on purpose.
While saving the configuration in a Python module is convenient, and often looks nicer, there is a caveat: a python module is after all
a programmable, running code. With an Ethereum development platform, that deals directly with money, we think
it's safer to put the configurations in static, non programmable, and external files.

The option to change the configuration dynamically is still available in run time, using the ``project.config`` property.
But otherwise, Populus configuration comes from static JSON files. What you see is what you get, no surprises.


What You Can Configure
^^^^^^^^^^^^^^^^^^^^^^

This config file controls many aspects of populus that are configurable.
Currently the config file controls the following things.

* Project root directory
* Contract source file location
* Compiler settings
* Available chains and how web3 connects to them.


Compiler Configuration
^^^^^^^^^^^^^^^^^^^^^^

Each complication backend takes settings that are passed down to Solidity compiler
Input Description (JSON) and command line.

Here is an example for the compilation backend settings when using
contract source files in folders outside of the Populus default ``./contracts``
folder.

.. code-block:: javascript

    {
      "compilation": {
        "contracts_source_dirs": [
          "./contracts",
          "/path-to-your-external-solidity-files",
        ],
        "backend": {
          "class": "populus.compilation.backends.SolcCombinedJSONBackend",
          "settings": {
              "stdin": {
                "optimizer": {
                  "enabled": true,
                  "runs": 500
                },
                "outputSelection": {
                  "*": {
                    "*": [
                      "abi",
                      "metadata",
                      "evm.bytecode",
                      "evm.deployedBytecode"
                    ]
                  }
                }
              },
              "command_line_options": {
                "allow_paths": "/path-to-your-external-solidity-files"
              }
            }
          }
        }
      }
    }


``backend.settings`` has two keys

* ``stdin`` is `Solidity Input Description as JSON <http://solidity.readthedocs.io/en/develop/using-the-compiler.html?highlight=input%20description#input-description>`_

* ``command_line_options`` are passed to Solidity compiler command line, as given keyword arguments to `py-solc` package's `solc.wrapper.solc_wrapper <https://github.com/ethereum/py-solc/blob/3a6de359dc31375df46418e6ffd7f45ab9567287/solc/wrapper.py#L20>_`

Contract Source Directory
"""""""""""""""""""""""""

The directory that project source files can be found in.

* key: ``compilation.contracts_source_dirs``
* value: List of filesystem paths
* default: ``['./contracts']``


Compiler Backend
""""""""""""""""

Set which compiler backend should be used

* key: ``compilation.backend.class``
* value: Dot separated python path
* default: ``populus.compilation.backends.SolcStandardJSONBackend``

Settings for the compiler backend

* key: ``compilation.backend.settings``
* value: Object of configuration parameters for the compiler backend.
* default: ``{"optimize": true, "output_values": ["abi", "bin", "bin-runtime", "devdoc", "metadata", "userdoc"]}``


Configuring compiler for extra
""""""""""""""""""""""""""""""

Set `solc import path remappings <https://github.com/ethereum/py-solc#import-path-remappings>`_. This is especially useful if you want to use libraries like `OpenZeppelin <https://github.com/OpenZeppelin/zeppelin-solidity/>`_ with your project. Then you can directly import Zeppelin contracts like ``import "zeppelin/contracts/token/TransferableToken.sol";``.

* key: ``compilation.import_remappings``
* value: Array of strings
* default: ``[]``
* example: ``["zeppelin=zeppelin"]`` assuming that the root directory for the Zeppelin contracts is ``./zeppelin`` in the root of your project.

Chains
^^^^^^

The ``chains`` key within the configuration file declares what chains populus
has access to, and how to connect to them.  Populus comes pre-configured with
the following chains.

* ``'mainnet'``: Connects to the public ethereum mainnet via ``geth``.
* ``'ropsten'``: Connects to the public ethereum ropsten testnet via ``geth``.
* ``'tester'``: Uses an ephemeral in-memory chain backed by pyethereum.
* ``'testrpc'``: Uses an ephemeral in-memory chain backed by pyethereum.
* ``'temp'``: Local private chain whose data directory is removed when the chain
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


Custom Chains Using the ExternalChain Class
-------------------------------------------

You can define your own custom chains. Custom chains should use the ``ExternalChain`` class,
which lets you access a Web3 provider. Web3 is the actual layer that connects to the running geth process,
and let Populus interact with the blockchain.

.. note::
  If you are familiar with web development, then you can think of
  Web3 as the underlying WSGI. In web development WSGI hooks to Apache or Nginx, here we have Web3 that hooks
  to geth.

The minimum configuration that Web3 requires are *either*:

* ``IPCProvider``: connects to geth via IPC, by the configured ``ipc_path``
* ``HTTPProvider``: connects via http or https to geth's rpc, by the configured ``endpoint_uri``

Here are two examples of a custom ``ExternalChain`` configuration.

IPC

.. code-block:: javascript

    "chains": {
      "horton": {
        "chain": {
          "class": "populus.chain.ExternalChain"
        },
        "web3": {
          "provider": {
            "class": "web3.providers.ipc.IPCProvider",
            "settings": {
              "ipc_path": "./chains/horton/geth.ipc"
            }
          }
        },
        ...
      }
    }

HTTP

.. code-block:: javascript

    "chains": {
      "local_chain": {
        "chain": {
          "class": "populus.chain.ExternalChain"
        },
        "web3": {
          "provider": {
            "class": "web3.providers.rpc.HTTPProvider",
            "settings": {
              "endpoint_uri": "https://127.0.0.1:8545"
            }
          }
        },
        ...
      }
    }


The important thing to remember is that Populus will **not** run geth for you. You will
have to run geth, and then Populus will use the chain configuration to connect to this **already running** process via Web3.
If you created a local chain with the ``$ populus chain new`` command, Populus will create an executable that you
can use to run the chain, see :ref:`running_local_blockchain`


In the next Populus version, all the chains will be configured as ``ExternalChain``

For more details on Web3, see the `Web3 documentation <https://web3py.readthedocs.io/en/latest/>`_ .


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

.. literalinclude:: ../populus/assets/defaults.v7.config.json
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
