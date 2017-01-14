Configuration
=============

.. contents:: :local:

Introduction
------------

Populus is designed to be highly configurable through the project configuration
file.  By default, populus will load the file name ``populus.json`` from the
root of your project.

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


Sub Configuration
^^^^^^^^^^^^^^^^^

Certain sections of the project configuration such as individual chain
configurations are treated as their own config object.  If looked up using the
above dictionary-like API the returned object will be a normal dictionary like
object which doesn't support nested key lookups.

.. code-block:: python

    >>> a = project.config['a']
    >>> a['b.c']
    KeyError: 'b.c'

In cases like these you should use the ``.get_config`` API.

.. code-block:: python

    >>> a = project.config.get_config('a')
    >>> a['b.c']
    'd'


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


Web3 Configuration
------------------

There are various parts of the application which require configuration a web3
instance to connect to a node.  Each web3 configuration has the following
configuration options.

Provider
^^^^^^^^

Configuration for the Web3 Provider 

Provider Class
""""""""""""""

Specifies the import path for the provider class that should be used.

* key: ``provider.class``
* value: Dot separated python path
* required: Yes

Provider Settings
"""""""""""""""""

Specifies the ``**kwargs`` that should be used when instantiating the provider.

* key: ``provider.settings``
* value: Key/Value mapping


Eth Module
^^^^^^^^^^

Configuration for the Web3 Eth Module

Default Account
"""""""""""""""

Sets the default account that will be used for the ``from`` address.

* key: ``eth.default_account``
* value: Ethereum Address


What you can Configure
----------------------

The following things can be configured via the project configuration file.


Compiler
^^^^^^^^

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

All chain configurations are found under the namespace ``chains``.  The
configuration for a chain named ``'local'`` would be found under the key
``chains.local``.

Is External
"""""""""""

Flag to specify if populus should manage running this chain.

* key: ``chains.<chain-name>.is_external``
* value: Boolean
* default: ``False``

Web3
""""""""""""""""""

Configuration for the Web3 instance this chain will use to connect to the blockchain.

* key: ``chains.<chain-name>.web3``
* value: Web3 Configuration
* required: Yes



Defaults
--------

Populus ships with many defaults which can be overridden as you see fit.

