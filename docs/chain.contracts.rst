.. _chain-contracts:

.. module:: populus.chain.base
.. currentmodule:: populus.chain.base

.. py:class:: BaseChain

Accessing Contracts
===================

The `~populus.chain.base.BaseChain` object is the entry point for three APIs
which collectively expose all of the raw compiler output from your project
contracts, the contract factory classes for each of your contracts, and the
deployed instances of those contracts.  These APIs are:

* The :ref:`Store API <chain-store>` gives access to both the raw compiler output from your contracts as well as the contract factories for your contracts.  This api can be accessed from the :attr:`BaseChain.store` property.
* The :ref:`Registrar API <chain-registrar>` records the addresses of deployed contract instances for later retrieval.  This api can be accessed from the :attr:`BaseChain.registrar` property.
* The :ref:`Provider API <chain-provider>` gives access to the deployed instances of your contracts.   This api can be accessed from the :attr:`BaseChain.provider` property.


Getting the raw compiled data
-----------------------------

To retrieve the contract data for a specific contract you will use the
:meth:`BaseChain.store.get_base_contract_factory` method.  Supposing that your
project contained a contract named "Math" you could retrieve the contract data
using the following code.

.. code-block:: python

    >>> chain.store.get_base_contract_factory('Math')
    {
      'abi': [...],
      'bytecode': '0x...',
      'bytecode_runtime': '0x...',
      'metadata': {...},
    }


You may also want to retrieve all of the contract data for your project.  This
can be done with the :meth:`BaseChain.store.get_all_contract_data` method.


.. code-block:: python

    >>> chain.store.get_all_contract_data()
    {
      'Math': {'abi': [...], ...},
      'MyOtherContract': {'abi': [...], ...},
    }


Getting contract factories
--------------------------

A contract factory is a python class which represents one of your project
contracts.  The "base" factory is the class returned by the
:meth:`chain.web3.contract` function.  The ``bytecode`` and
``bytecode_runtime`` values for a base contract will not be linked.  You can
retrieve a the base contract factory with the
:meth:`BaseChain.store.get_base_contract_factory` method.

.. code-block:: python

    >>> Math = chain.store.get_base_contract_factory('Math')
    >>> Math.abi
    [...]
    >>> Math.bytecode
    "0x..."
    >>> Math.bytecode_runtime
    "0x..."


In most situations you will want the returned factory to have it's bytecode
linked.  Use the :meth:`BaseChain.store.get_contract_factory` method.

.. code-block:: python

    >>> Math = chain.store.get_contract_factory('Math')
    >>> Math.abi
    [...]
    >>> Math.bytecode
    "0x..."
    >>> Math.bytecode_runtime
    "0x..."
