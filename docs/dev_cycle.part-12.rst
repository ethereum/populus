Part 12: API
============

.. contents:: :local:


Usage
-----

Populus is a versatile tool, designed to help you from the moment you start do develop a smart contract, until it's working
and integrated in any Python project. The core of Populus is a Pythonic interface and command line tools
to the Ethereum platform.

The main areas you will use Populus are:

**[1]** Smart Contracts Development: manage and work with your blockchain assets, the Solidity source files,
compilation data, deployments etc

**[2]** Testing: a testing framework with py.test, ``tester`` chains, and py.test fixtures

**[3]** Integration to any Python project and application: with the Pythonic API

So far we covered the contract development, deployments, and testing.  We touched the API with a few simple scripts.
In this part, we will cover the important classes of the  API,
and describe a few important members of each class.

Orientation
-----------

Typically your entry point to the API is a ``Project`` object. From the project object
you get a chain object, and from a chain object you get a contract object. Then you can
work with this contract.

The chain also has a ``web3`` property with the full Web3.py API.

Why do we need a ``chain`` abstraction at all? Because it enables the core Populus idea,
to work with contracts in *every* state:
the source files, the compiled data, and the deployed contract instances on one or more chains.

True, Solidity source files and compiled data are *not* chain related, only the deployed instances on a given
chain are. But when you call a contract from a ``chain``, Populus will either find the instance on that chain, or
compiles and deploys a new instance. Similar code is used regardless of the contract's state. E.g., the same code
is used when Populus needs to re-deploy on each test run with the ``tester`` chain, and
when you interact with a persistent contract instance on a local chain or ``mainnet``.

So with the ``chain`` object, you have one consistent interface, no matter what the underlying
contract state is. See :ref:`what is a contract <what_is_a_contract>`


Project
-------

.. py:module:: populus.project
.. py:class:: Project


The ``Project`` object is the main entry point to the Populus API.

Existing Project:

.. code-block:: python

    from populus.project import Project
    # the directory should have a project.json file
    p = Project(project_dir='/home/mary/project/donations')

New Project:

.. code-block:: python

    from populus.project import Project
    # will create a new project.json file
    # will not create the default project structure you get with the command line populus init
    p = Project(project_dir='/home/mary/project/donations')


PopulusContract
---------------

.. py:module:: populus.contracts.provider
.. py:class:: PopulusContract

A subclass of ``web3.contract.Contract``.
It is a Python object, with Python methods, that lets you interact with a corresponding
contract instance on a blockchain.

Usually you will not instantiate it directly, but will get it from a contract factory. Populus
keeps track of deployments, addresses, compiled data, abi, etc, and uses this info to create the
``PopulusContract`` for you.


Chain
-----

.. py:module:: populus.chain.base
.. py:class:: BaseChain


The ``chain`` object is a Python object that corresponds to a running blockchain.

Get the chain from a project object in a context manager:

.. code-block:: python

    # for a chain name as it appears in the config
    with p.get_chain('chainname') as chain:
        # chain object available here inside the context manager


``chainname`` is any chain that is defined either (a) in the project config file, ``project.json``, or (b) in the user-scope
config file at ``~/.populus/config.json``.

In both files, the chain settings appears under the ``chains`` key.

.. note::

    If the same chain name appears in both the project config and the user config,
    the project config name will override the user-scope config


Chain Classes
''''''''''''''

.. py:module:: populus.chain.external
.. py:class:: ExternalChain

A chain object over a running local instance of geth. The default chain when you don't
use a chain for tests

.. py:module:: populus.chain.tester
.. py:class:: TesterChain

An ephemeral chain that saves data to memory and resets on every run, great for testing
(similar to a blank slate DB for each test run)

.. py:module:: populus.chain.testrpc
.. py:class:: TestRPCChain

Local chain with RPC client, for fast RPC response in testing

Web3
----

Full Web3 API to the running chain

.. code-block:: python

    w3 = chain.web3


Provider
--------

.. py:module:: populus.contracts.provider
.. py:class:: Provider


The ``Provider`` object is the handle to a *contract factory*. It is capable of handling all the possible
states of a contract, and using a contract factory,  returns a ``PopulusContract``.

To get a provider:

.. code-block:: python

    prv = chain.provider


.. py:attribute::  provider.get_contract(...)

Returns: ``PopulusContract``

Tries to find a contract in the registrar, if exist, will verify the bytecode and return
a ``PopulusContract``

.. note::

    Currently matching bytecode is only by the current installed solc version


.. py:attribute::  provider.get_or_deploy_contract(...)

Returns: ``PopulusContract``

Perhaps the most powerful line in the Populus API

**[1]** If the contract's is *already* deployed, same as ``get_contract``

**[2]** If the contract is *not* deployed, Populus will compile it, prepare a deployment transaction,
calculate the gas estimate, send and wait for the deployment to a new address,
verify the byte code, saves the deployment details to the registrar, and *then* create the Python
contract object that corresponds to this address and return it.


.. py:attribute:: def get_contract_data ("contract_identifier")

Returns a dictionary with the contract's data: abi, bytecode, etc.


Registrar
---------

.. py:module:: populus.contracts.registrar
.. py:class:: Registrar

A handler of contracts instances and addresses on chains.


.. py:attribute:: def set_contract_address(...)

set a contract address in the registrar


.. py:attribute:: get_contract_addresses (...)

Retrieve a contract address in the registrar



Config
------

.. py:module:: populus.config.base
.. py:class:: Config

The ``Config`` class is a "magic" object. It behaves like a dictionary, but knows how to unpack
nested keys:

.. code-block:: python

    >>> from populus.project import Project
    >>> p = Project('/home/mary/projects/donations')
    >>> p.config
    {'chains': {'web3http': {'web3': {'foo': 'baz'}, 'chain': {'class': ....
    >>> p.config.keys()
    ('chains', 'web3', 'compilation', 'contracts', 'version')
    >>> type(p.config)
    <class 'populus.config.base.Config'>
    >>> p.config.get('chains')
    {'web3http': {'web3': {}, 'chain': {cts.backends.testing: 50}, 'ProjectContracts'....
    >>> p.config.get('chains.web3http')
    {'web3': {}, 'chain': {'class': 'populus.chain.web3provider.Web3HTTPProviderChain'}.....
    >>> p.config.get('chains.web3http.web3')
    {}
    >>> p.config['chains.web3http.web3'] = {'foo':'baz'}
    >>> p.config.get('chains.web3http.web3')
    {'foo': 'baz'}
    >>> p.config.get('chains.web3http.web3.foo')
    'baz'

Usually you don't initiate a ``Config`` object yourself, but use an existing object that Populus
built from the configuration files. Then use common dictionary methods, which are implemented in the
``Config`` class.

.. py:attribute:: items()

Retrieves the top level keys, so the ``value`` can be another nested config

.. py:attribute:: items(flatten=True)

Retrieves the full path.

.. code-block:: python

    >>> p.config.items()
    (('chains', {'web3http': {'web3': {'foo': 'baz'}, 'chain': {'class': 'populus.chain.web3provider ....
    >>> p.config.items(flatten=True)
    (('chains.horton.chain.class', 'populus.chain.ExternalChain'), ('chains ...



Populus Configs Usage
'''''''''''''''''''''

.. py:attribute:: proj_obj.project_config

    The configuration loaded from the project local config file, ``project.json``

.. py:attribute:: proj_obj.user_config

    The configuration loaded from the user config file, ``~/.populus/config.json``

.. py:attribute:: proj_obj.config

    The merged ``project_config`` and ``user_config``: when ``project_config`` and ``user_config``
    has the *same* key, the ``project_config`` overrides ``user_config``, and the key value in the
    merged ``project.config`` will be that of ``project_config``


.. py:attribute:: proj_obj.get_chain_config(...)

    The chain configuration

.. py:attribute:: chain_obj.get_web3_config

    The chain's Web3 configuration

.. py:attribute:: proj_obj.reload_config()

    Reloads configuration from ``project.json`` and ``~/.populus/config.json``. You should instantiate the chain
    objects after reload.



Assignment &  Persistency
'''''''''''''''''''''''''

Populus initial configuration is loaded from the JSON files.

You can customise the config keys in runtime, but these changes are *not* persistent and will *not* be saved. The next time
Populus run, the configs will reset to ``project.json`` and ``~/.populus/config.json``.

Assignment of simple values works like any dictionary:


.. code-block:: python

    project_obj.config["chains.my_tester.chain.class"] = "populus.chain.tester.TesterChain"


However, since config is nested, you can assign a dictionary, or another config object, to a key:

.. code-block:: python

    project_obj.config["chains.my_tester.chain"] = {"class":"populus.chain.tester.TesterChain"}

You can even keep a another separate configuration file, and replace the entire project config
in runtime, e.g. for testing, running in different environments, etc:

.. code-block:: python

    from populus.config import load_config
    proj_object.config = load_config("path/to/another/config.json")

Reset all changes back to the default:

.. code-block:: python

    proj_obj.reload_config()

You will have to re-instantiate chains after the reload.

.. note::

    JSON files may seem odd if you are used to
    Python settings files (like django), but we think that for blockchain development, the external,
    static files are safer than a programmable Python module.




JSON References
'''''''''''''''

There is a caveat: ``config_obj['foo.baz']`` may not return the same value is ``config_obj.get('foo.baz')``.
The reason is that the configuration files are loaded as JSON schema, which allows ``$ref$``.
So if the config is:

.. code-block:: javascript

    {'foo':{'baz':{'$ref':'fawltyTowers'}}}

And in another place on the file you have:

.. code-block:: javascript

    'fawltyTowers':['Basil','Sybil','Polly','Manual']

Then:

.. code-block:: python

   >>> config_obj['foo.baz'] # doesn't solve $ref
   {'$ref':'fawltyTowers'}
   >>> config_obj.get('foo.baz') # solves $ref
   ['Basil','Sybil','Polly','Manual']

To avoid this, if you assign your own config_obj, use ``config_obj.unref()``, which will solve
all of the references.


Backends
--------

Populus is pluggable, using backend. The interface is defined in a base class, and a
backend can override or implement part or all this functionality.

E.g., the default backend for the
``Registrar`` is the ``JSONFileBackend``, which saves the deployments details to a JSON file.
But if you would need to save these details to RDBMS, you can write your own backend, and as long as
it implements the ``Registrar`` functions (``set_contract_address``, ``get_contract_addresses``)
it will work.


Contracts backends:

.. py:module:: populus.contracts.filesystem
.. py:class:: JSONFileBackend

``is_provider: False``,
``is_registrar: True``

Saves registrar details to a JSON file

.. py:module:: populus.contracts.filesystem
.. py:class:: MemoryBackend

``is_provider: False``,
``is_registrar: True``

Saves registrar details to memory, in a simple dict variable


.. py:module:: populus.contracts.project
.. py:class:: ProjectContractsBackend

``is_provider: True``,
``is_registrar: False``

Gets the contracts data from the project source dirs

.. py:module:: populus.contracts.testing
.. py:class:: TestContractsBackend

``is_provider: True``,
``is_registrar: False``

Gets the contracts data from the project tests dir
